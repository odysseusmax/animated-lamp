import os
import uuid
import time
import shlex
import shutil
import asyncio
import logging
import datetime
import traceback

from async_timeout import timeout

from ..config import Config


log = logging.getLogger(__name__)


class Sample:
    async def sample_fn(self, c, m):
        chat_id = m.from_user.id
        if c.CURRENT_PROCESSES.get(chat_id, 0) == Config.MAX_PROCESSES_PER_USER:
            await m.answer('You have reached the maximum parallel processes! Try again after one of them finishes.', show_alert=True)
            return
        await m.answer()
        if not c.CURRENT_PROCESSES.get(chat_id):
            c.CURRENT_PROCESSES[chat_id] = 0
        c.CURRENT_PROCESSES[chat_id] += 1

        media_msg = m.message.reply_to_message
        if media_msg.empty:
            await m.edit_message_text(text='Why did you delete the file 😠, Now i cannot help you 😒.')
            c.CURRENT_PROCESSES[chat_id] -= 1
            return

        uid = str(uuid.uuid4())
        output_folder = Config.SMPL_OP_FLDR.joinpath(uid)
        os.makedirs(output_folder, exist_ok=True)

        if Config.TRACK_CHANNEL:
            tr_msg = await media_msg.forward(Config.TRACK_CHANNEL)
            await tr_msg.reply_text(f"User id: `{chat_id}`")

        if media_msg.media:
            file_link = self.generate_stream_link(media_msg)
        else:
            file_link = media_msg.text

        await m.edit_message_text(text='😀 Generating Sample Video! This might take some time.')

        try:
            async with timeout(Config.TIMEOUT):
                start_time = time.time()
                duration = await self.get_duration(file_link)
                if isinstance(duration, str):
                    await m.edit_message_text(text="😟 Sorry! I cannot open the file.")
                    l = await media_msg.forward(Config.LOG_CHANNEL)
                    await l.reply_text(f'stream link : {file_link}\n\nSample video requested\n\n{duration}', True)
                    c.CURRENT_PROCESSES[chat_id] -= 1
                    shutil.rmtree(output_folder, ignore_errors=True)
                    return

                reduced_sec = duration - int(duration*10 / 100)
                sample_duration = await c.db.get_sample_duration(chat_id)

                start_at = self.get_random_start_at(reduced_sec, sample_duration)

                sample_file = output_folder.joinpath(f'sample_video.mkv')
                subtitle_option = await self.fix_subtitle_codec(file_link)

                log.info(f"Generating sample video (duration {sample_duration}s from {start_at}) from location: {file_link} for {chat_id}")

                ffmpeg_cmd = ['ffmpeg', '-headers', f'IAM:{Config.IAM_HEADER}', '-hide_banner', '-ss', str(start_at), '-i', file_link, '-t',
                              str(sample_duration), '-map', '0', '-c', 'copy']
                if subtitle_option:
                    ffmpeg_cmd += subtitle_option
                ffmpeg_cmd.append(str(sample_file))

                log.debug(ffmpeg_cmd)
                output = await self.run_subprocess(ffmpeg_cmd)
                log.debug(output)

                if (not sample_file.exists()) or (os.path.getsize(sample_file) == 0):
                    await m.edit_message_text(text='😟 Sorry! Sample video generation failed possibly due to some infrastructure failure 😥.')
                    ffmpeg_output = output[0].decode() + '\n' + output[1].decode()
                    l = await media_msg.forward(Config.LOG_CHANNEL)
                    await l.reply_text(f'stream link : {file_link}\n\n duration {sample_duration} sample video generation failed\n\n{ffmpeg_output}', True)
                    c.CURRENT_PROCESSES[chat_id] -= 1
                    shutil.rmtree(output_folder, ignore_errors=True)
                    return

                thumb = await self.generate_thumbnail_file(sample_file, uid)

                await m.edit_message_text(text=f'🤓 Sample video was generated successfully!, Now starting to upload!')

                await media_msg.reply_chat_action("upload_video")

                await media_msg.reply_video(
                        video=str(sample_file),
                        quote=True,
                        caption=f"Sample video. {sample_duration}s from {datetime.timedelta(seconds=start_at)}",
                        duration=sample_duration,
                        thumb=thumb,
                        supports_streaming=True
                    )

                await m.edit_message_text(text=f'Successfully completed process in {datetime.timedelta(seconds=int(time.time()-start_time))}\n\nIf You find me helpful, please rate me [here](tg://resolve?domain=botsarchive&post=1206).')

        except (asyncio.TimeoutError, asyncio.CancelledError):
            await m.edit_message_text(text='😟 Sorry! Video trimming failed due to timeout. Your process was taking too long to complete, hence cancelled')
        except Exception as e:
            log.error(e, exc_info=True)
            await m.edit_message_text(text='😟 Sorry! Sample video generation failed possibly due to some infrastructure failure 😥.')
            l = await media_msg.forward(Config.LOG_CHANNEL)
            await l.reply_text(f'sample video requested and some error occoured\n\n{traceback.format_exc()}', True)
        finally:
            c.CURRENT_PROCESSES[chat_id] -= 1
            shutil.rmtree(output_folder, ignore_errors=True)
