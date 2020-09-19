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
from .utils import generate_stream_link, get_duration, get_random_start_at, get_dimentions, run_subprocess


log = logging.getLogger(__name__)


async def screenshot_fn(c, m):
    chat_id = m.from_user.id
    if c.CURRENT_PROCESSES.get(chat_id, 0) == Config.MAX_PROCESSES_PER_USER:
        await m.answer('You have reached the maximum parallel processes! Try again after one of them finishes.', show_alert=True)
        return

    await m.answer()
    if not c.CURRENT_PROCESSES.get(chat_id):
        c.CURRENT_PROCESSES[chat_id] = 0
    c.CURRENT_PROCESSES[chat_id] += 1

    _, num_screenshots = m.data.split('+')
    num_screenshots = int(num_screenshots)
    media_msg = m.message.reply_to_message
    if media_msg.empty:
        await m.edit_message_text(text='Why did you delete the file 😠, Now i cannot help you 😒.')
        c.CURRENT_PROCESSES[chat_id] -= 1
        return

    uid = str(uuid.uuid4())
    output_folder = Config.SCRST_OP_FLDR.joinpath(uid)
    os.makedirs(output_folder, exist_ok=True)

    if Config.TRACK_CHANNEL:
        tr_msg = await media_msg.forward(Config.TRACK_CHANNEL)
        await tr_msg.reply_text(f"User id: `{chat_id}`")

    try:
        def ratio(x, y):
            gcd = lambda m,n: m if not n else gcd(n,m%n)
            d = gcd(x, y)
            return x/d, y/d

        async with timeout(Config.TIMEOUT) as cm:
            start_time = time.time()

            await m.edit_message_text(text='Processing your request, Please wait! 😴')

            if media_msg.media:
                file_link = generate_stream_link(media_msg)
            else:
                file_link = media_msg.text

            await m.edit_message_text(text='😀 Generating screenshots!')

            duration = await get_duration(file_link)
            if isinstance(duration, str):
                await m.edit_message_text(text="😟 Sorry! I cannot open the file.")
                l = await media_msg.forward(Config.LOG_CHANNEL)
                await l.reply_text(f'stream link : {file_link}\n\nRequested screenshots: {num_screenshots}.\n\n{duration}', True)
                c.CURRENT_PROCESSES[chat_id] -= 1
                shutil.rmtree(output_folder)
                return

            log.info(f"Generating {num_screenshots} screenshots from location: {file_link} for {chat_id}")

            reduced_sec = duration - int(duration*2 / 100)
            screenshots = []
            watermark = await c.db.get_watermark_text(chat_id)
            watermark_color_code = await c.db.get_watermark_color(chat_id)
            watermark_color = Config.COLORS[watermark_color_code]
            as_file = await c.db.is_as_file(chat_id)
            screenshot_mode = await c.db.get_screenshot_mode(chat_id)
            font_size = await c.db.get_font_size(chat_id)
            ffmpeg_errors = ''

            if screenshot_mode == 0:
                screenshot_secs = [int(reduced_sec/num_screenshots)*i for i in range(1, 1+num_screenshots)]
            else:
                screenshot_secs = [get_random_start_at(reduced_sec) for i in range(1, 1+num_screenshots)]

            width, height = await get_dimentions(file_link)
            fontsize = round((math.sqrt( width**2 + height**2 ) / 1388.0) * Config.FONT_SIZES[font_size])
            a_ratio = ratio(width, height)
            x_fact = 2
            x_pos = round((width*x_fact) / 100)
            y_pos = round((x_pos * a_ratio[1])/a_ratio[0])

            for i, sec in enumerate(screenshot_secs):
                thumbnail_template = output_folder.joinpath(f'{i+1}.png')
                ffmpeg_cmd = f"ffmpeg -hide_banner -ss {sec} -i {shlex.quote(file_link)} -vf \"drawtext=fontcolor={watermark_color}:fontsize={fontsize}:x={x_pos}:y=H-th-{y_pos}:text='{shlex.quote(watermark)}', scale=1280:-1\" -y  -vframes 1 '{thumbnail_template}'"
                output = await run_subprocess(ffmpeg_cmd)
                log.debug(output)
                await m.edit_message_text(text=f'😀 `{i+1}` of `{num_screenshots}` generated!')
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
                await m.edit_message_text(text='😟 Sorry! Screenshot generation failed possibly due to some infrastructure failure 😥.')
                l = await media_msg.forward(Config.LOG_CHANNEL)
                if ffmpeg_errors:
                    error_file = io.StringIO()
                    error_file.name = f"{uid}-errors.txt"
                    error_file.write(ffmpeg_errors)
                    await l.reply_document(error_file, caption=f"stream link : {file_link}\n\n{num_screenshots} screenshots where requested and Screen shots where not generated.")
                else:
                    await l.reply_text(f'stream link : {file_link}\n\n{num_screenshots} screenshots where requested and Screen shots where not generated.', True)
                c.CURRENT_PROCESSES[chat_id] -= 1
                shutil.rmtree(output_folder)
                return

            await m.edit_message_text(text=f'🤓 You requested {num_screenshots} screenshots and {len(screenshots)} screenshots generated, Now starting to upload!')

            await media_msg.reply_chat_action("upload_photo")

            if as_file:
                aws = [media_msg.reply_document(quote=True, **photo) for photo in screenshots]
                await asyncio.gather(*aws)
            else:
                await media_msg.reply_media_group(screenshots, True)
            await m.edit_message_text(text=f'Successfully completed process in {datetime.timedelta(seconds=int(time.time()-start_time))}\n\nIf You find me helpful, please rate me [here](tg://resolve?domain=botsarchive&post=1206),')
    except (asyncio.TimeoutError, asyncio.CancelledError):
        await m.edit_message_text(text='😟 Sorry! Video trimming failed due to timeout. Your process was taking too long to complete, hence cancelled')
    except Exception as e:
        log.error(e, exc_info=True)
        await m.edit_message_text(text='😟 Sorry! Screenshot generation failed possibly due to some infrastructure failure 😥.')

        l = await media_msg.forward(Config.LOG_CHANNEL)
        await l.reply_text(f'{num_screenshots} screenshots where requested and some error occoured\n\n{traceback.format_exc()}', True)
    finally:
        c.CURRENT_PROCESSES[chat_id] -= 1
        shutil.rmtree(output_folder)
