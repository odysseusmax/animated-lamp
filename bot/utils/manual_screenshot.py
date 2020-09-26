import os
import io
import uuid
import time
import math
import shlex
import shutil
import asyncio
import logging
import datetime
import traceback

from pyrogram.types import InputMediaPhoto
from async_timeout import timeout

from ..config import Config


log = logging.getLogger(__name__)


class ManualScreenshot:
    async def manual_screenshot_fn(self, c, m):

        chat_id = m.chat.id
        if c.CURRENT_PROCESSES.get(chat_id, 0) == Config.MAX_PROCESSES_PER_USER:
            await m.reply_text('You have reached the maximum parallel processes! Try again after one of them finishes.', True)
            return
        if not c.CURRENT_PROCESSES.get(chat_id):
            c.CURRENT_PROCESSES[chat_id] = 0
        c.CURRENT_PROCESSES[chat_id] += 1

        message = await c.get_messages(
            chat_id,
            m.reply_to_message.message_id
        )
        await m.reply_to_message.delete()
        media_msg = message.reply_to_message

        if media_msg.empty:
            await m.reply_text('Why did you delete the file 😠, Now i cannot help you 😒.', True)
            c.CURRENT_PROCESSES[chat_id] -= 1
            return

        try:
            raw_user_input = [int(i.strip()) for i in m.text.split(',')]
        except:
            await m.reply_text('Please follow the specified format', True)
            c.CURRENT_PROCESSES[chat_id] -= 1
            return

        uid = str(uuid.uuid4())
        output_folder = Config.SCRST_OP_FLDR.joinpath(uid)
        os.makedirs(output_folder, exist_ok=True)

        if Config.TRACK_CHANNEL:
            tr_msg = await media_msg.forward(Config.TRACK_CHANNEL)
            await tr_msg.reply_text(f"User id: `{chat_id}`")

        snt = await m.reply_text('Processing your request, Please wait! 😴', True)

        try:
            async with timeout(Config.TIMEOUT) as cm:
                start_time = time.time()

                if media_msg.media:
                    file_link = self.generate_stream_link(media_msg)
                else:
                    file_link = media_msg.text

                duration = await self.get_duration(file_link)
                if isinstance(duration, str):
                    await snt.edit_text("😟 Sorry! I cannot open the file.")
                    l = await media_msg.forward(Config.LOG_CHANNEL)
                    await l.reply_text(f'stream link : {file_link}\n\nRequested manual screenshots\n\n{duration}', True)
                    c.CURRENT_PROCESSES[chat_id] -= 1
                    shutil.rmtree(output_folder, ignore_errors=True)
                    return

                valid_positions = []
                invalid_positions = []
                for pos in raw_user_input:
                    if pos<0 or pos>duration:
                        invalid_positions.append(str(pos))
                    else:
                        valid_positions.append(pos)

                if not valid_positions:
                    await snt.edit_text("😟 Sorry! None of the given positions where valid!")
                    c.CURRENT_PROCESSES[chat_id] -= 1
                    shutil.rmtree(output_folder, ignore_errors=True)
                    return

                if len(valid_positions) > 10:
                    await snt.edit_text(f"😟 Sorry! Only 10 screenshots can be generated. Found {len(valid_positions)} valid positions in your request")
                    c.CURRENT_PROCESSES[chat_id] -= 1
                    shutil.rmtree(output_folder, ignore_errors=True)
                    return

                if invalid_positions:
                    invalid_position_str = ', '.join(invalid_positions)
                    txt = f"Found {len(invalid_positions)} invalid positions ({invalid_position_str}).\n\n😀 Generating screenshots after ignoring these!."
                else:
                    txt = '😀 Generating screenshots!.'

                await snt.edit_text(txt)

                screenshots = []
                ffmpeg_errors = ''
                as_file = await c.db.is_as_file(chat_id)
                watermark = await c.db.get_watermark_text(chat_id)
                if watermark:
                    watermark_color_code = await c.db.get_watermark_color(chat_id)
                    watermark_color = Config.COLORS[watermark_color_code]
                    watermark_position = await c.db.get_watermark_position(chat_id)
                    font_size = await c.db.get_font_size(chat_id)
                    width, height = await self.get_dimentions(file_link)
                    fontsize = int((math.sqrt( width**2 + height**2 ) / 1388.0) * Config.FONT_SIZES[font_size])
                    x_pos, y_pos = self.get_watermark_coordinates(watermark_position, width, height)
                    watermark_options = f'drawtext=fontcolor={watermark_color}:fontsize={fontsize}:x={x_pos}:y={y_pos}:text={watermark}, scale=1280:-1'

                log.info(f"Generating screenshots at positions {valid_positions} from location: {file_link} for {chat_id}")

                for i, sec in enumerate(valid_positions):
                    thumbnail_template = output_folder.joinpath(f'{i+1}.png')
                    ffmpeg_cmd = ['ffmpeg', '-headers', f'IAM:{Config.IAM_HEADER}', '-hide_banner', '-ss', str(sec), '-i', file_link,'-vf']
                    if watermark:
                        ffmpeg_cmd.append(watermark_options)
                    else:
                        ffmpeg_cmd.append('scale=1280:-1')
                    ffmpeg_cmd += ['-y', '-vframes', '1', str(thumbnail_template)]

                    log.debug(ffmpeg_cmd)
                    output = await self.run_subprocess(ffmpeg_cmd)
                    log.debug(output)
                    await snt.edit_text(f'😀 `{i+1}` of `{len(valid_positions)}` generated!')
                    if thumbnail_template.exists():
                        if as_file:
                            screenshots.append({
                                'document':str(thumbnail_template),
                                'caption':f"ScreenShot at {datetime.timedelta(seconds=sec)}"
                            })
                        else:
                            screenshots.append(
                                InputMediaPhoto(
                                    str(thumbnail_template),
                                    caption=f"ScreenShot at {datetime.timedelta(seconds=sec)}"
                                )
                            )
                        continue
                    ffmpeg_errors += output[0].decode() + '\n' + output[1].decode() + '\n\n'

                if not screenshots:
                    await snt.edit_text('😟 Sorry! Screenshot generation failed possibly due to some infrastructure failure 😥.')
                    l = await media_msg.forward(Config.LOG_CHANNEL)
                    if ffmpeg_errors:
                        error_file = io.BytesIO()
                        error_file.name = f"{uid}-errors.txt"
                        error_file.write(ffmpeg_errors.encode())
                        await l.reply_document(error_file, caption=f"stream link : {file_link}\n\nmanual screenshots {raw_user_input}.")
                    else:
                        await l.reply_text(f'stream link : {file_link}\n\nmanual screenshots {raw_user_input}.', True)
                    c.CURRENT_PROCESSES[chat_id] -= 1
                    shutil.rmtree(output_folder, ignore_errors=True)
                    return

                await snt.edit_text(text=f'🤓 You requested {len(valid_positions)} screenshots and {len(screenshots)} screenshots generated, Now starting to upload!')

                await media_msg.reply_chat_action("upload_photo")

                if as_file:
                    aws = [media_msg.reply_document(quote=True, **photo) for photo in screenshots]
                    await asyncio.gather(*aws)
                else:
                    await media_msg.reply_media_group(screenshots, True)

                await snt.edit_text(f'Successfully completed process in {datetime.timedelta(seconds=int(time.time()-start_time))}\n\nIf You find me helpful, please rate me [here](tg://resolve?domain=botsarchive&post=1206).')
        except (asyncio.TimeoutError, asyncio.CancelledError):
            await snt.edit_text('😟 Sorry! Video trimming failed due to timeout. Your process was taking too long to complete, hence cancelled')
        except Exception as e:
            log.error(e, exc_info=True)
            await snt.edit_text('😟 Sorry! Screenshot generation failed possibly due to some infrastructure failure 😥.')
            l = await media_msg.forward(Config.LOG_CHANNEL)
            await l.reply_text(f'manual screenshots ({raw_user_input}) where requested and some error occoured\\n{traceback.format_exc()}', True)
        finally:
            c.CURRENT_PROCESSES[chat_id] -= 1
            shutil.rmtree(output_folder, ignore_errors=True)

