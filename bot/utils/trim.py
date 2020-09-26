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


class Trim:
    async def trim_fn(self, c, m):
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
            start, end = [int(i) for i in m.text.split(':')]
        except:
            await m.reply_text('Please follow the specified format', True)
            c.CURRENT_PROCESSES[chat_id] -= 1
            return

        if (start >= end) or (start < 0):
            await m.reply_text('Invalid range!', True)
            c.CURRENT_PROCESSES[chat_id] -= 1
            return

        request_duration = end-start

        if request_duration > Config.MAX_TRIM_DURATION:
            await m.reply_text(f'Please provide any range that\'s upto {Config.MAX_TRIM_DURATION}s. Your requested range **{start}:{end}** is `{request_duration}s` long!', True)
            c.CURRENT_PROCESSES[chat_id] -= 1
            return

        uid = str(uuid.uuid4())
        output_folder = Config.SMPL_OP_FLDR.joinpath(uid)
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

                await snt.edit_text('😀 Trimming Your Video! This might take some time.')

                duration = await self.get_duration(file_link)
                if isinstance(duration, str):
                    await snt.edit_text("😟 Sorry! I cannot open the file.")
                    l = await media_msg.forward(Config.LOG_CHANNEL)
                    await l.reply_text(f'stream link : {file_link}\n\ntrim video requested\n\n{start}:{end}\n\n{duration}', True)
                    c.CURRENT_PROCESSES[chat_id] -= 1
                    shutil.rmtree(output_folder, ignore_errors=True)
                    return

                if (start>=duration) or (end>=duration):
                    await snt.edit_text("😟 Sorry! The requested range is out of the video's duration!.")
                    c.CURRENT_PROCESSES[chat_id] -= 1
                    shutil.rmtree(output_folder, ignore_errors=True)
                    return

                log.info(f"Trimming video (duration {request_duration}s from {start}) from location: {file_link} for {chat_id}")

                sample_file = output_folder.joinpath(f'trim_video.mkv')
                subtitle_option = await self.fix_subtitle_codec(file_link)

                ffmpeg_cmd = ['ffmpeg', '-headers', f'IAM:{Config.IAM_HEADER}', '-hide_banner', '-ss', str(start), '-i', file_link, '-t',
                              str(request_duration), '-map', '0', '-c', 'copy']
                if subtitle_option:
                    ffmpeg_cmd += subtitle_option
                ffmpeg_cmd.append(str(sample_file))

                log.debug(ffmpeg_cmd)
                output = await self.run_subprocess(ffmpeg_cmd)
                log.debug(output)

                if (not sample_file.exists()) or (os.path.getsize(sample_file) == 0):
                    await snt.edit_text('😟 Sorry! video trimming failed possibly due to some infrastructure failure 😥.')
                    ffmpeg_output = output[0].decode() + '\n' + output[1].decode()
                    l = await media_msg.forward(Config.LOG_CHANNEL)
                    await l.reply_text(f'stream link : {file_link}\n\nVideo trim failed.\n\n{start}:{end}\n\n{ffmpeg_output}', True)
                    c.CURRENT_PROCESSES[chat_id] -= 1
                    shutil.rmtree(output_folder, ignore_errors=True)
                    return

                thumb = await self.generate_thumbnail_file(sample_file, uid)

                await snt.edit_text('🤓 Video trimmed successfully!, Now starting to upload!')

                await m.reply_chat_action("upload_video")

                await m.reply_video(
                    video=str(sample_file),
                    quote=True,
                    caption=f"Trimmed video from {datetime.timedelta(seconds=start)} to {datetime.timedelta(seconds=end)}",
                    duration=request_duration,
                    thumb=thumb,
                    supports_streaming=True
                )

                await snt.edit_text(f'Successfully completed process in {datetime.timedelta(seconds=int(time.time()-start_time))}\n\nIf You find me helpful, please rate me [here](tg://resolve?domain=botsarchive&post=1206).')

        except (asyncio.TimeoutError, asyncio.CancelledError):
            await snt.edit_text('😟 Sorry! Video trimming failed due to timeout. Your process was taking too long to complete, hence cancelled')
        except Exception as e:
            log.error(e, exc_info=True)
            await snt.edit_text('😟 Sorry! Video trimming failed possibly due to some infrastructure failure 😥.')
            l = await media_msg.forward(Config.LOG_CHANNEL)
            await l.reply_text(f'trim video requested and some error occoured\n\n{traceback.format_exc()}', True)
        finally:
            c.CURRENT_PROCESSES[chat_id] -= 1
            shutil.rmtree(output_folder, ignore_errors=True)
