import os
import time
import logging
import tempfile
import datetime

from bot.config import Config
from bot.utils import Utilities
from bot.messages import Messages as ms
from bot.database import Database
from .exception import BaseException
from .base import BaseProcess


log = logging.getLogger(__name__)
db = Database()


class SampleVideoProcessFailure(BaseException):
    pass


class SampleVideoProcess(BaseProcess):
    async def set_media_message(self):
        self.media_message = self.input_message.message.reply_to_message

    async def cancelled(self):
        await self.input_message.edit_message_text(ms.PROCESS_TIMEOUT)

    async def process(self):
        async def upload_notify(*args):
            await self.client.send_chat_action(self.chat_id, "upload_video")

        await self.set_media_message()
        await self.input_message.edit_message_text(ms.PROCESSING_REQUEST)
        try:
            if self.media_message.empty:
                raise SampleVideoProcessFailure(
                    for_user=ms.MEDIA_MESSAGE_DELETED,
                    for_admin=ms.MEDIA_MESSAGE_DELETED,
                )

            await self.track_user_activity()

            await self.input_message.edit_message_text(
                text=ms.SAMPLE_VIDEO_PROCESS_START
            )
            start_time = time.time()
            duration = await Utilities.get_duration(self.file_link)
            if isinstance(duration, str):
                raise SampleVideoProcessFailure(
                    for_user=ms.CANNOT_OPEN_FILE,
                    for_admin=ms.SAMPLE_VIDEO_PROCESS_OPEN_ERROR.format(
                        file_link=self.file_link, duration=duration
                    ),
                )

            reduced_sec = duration - int(duration * 10 / 100)
            sample_duration = await db.get_sample_duration(self.chat_id)
            temp_output_folder = tempfile.TemporaryDirectory()
            temp_thumbnail_folder = tempfile.TemporaryDirectory()
            with temp_output_folder as output_folder, temp_thumbnail_folder as thumbnail_folder:
                sample_file = os.path.join(output_folder, "sample_video.mkv")
                start_at = Utilities.get_random_start_at(reduced_sec, sample_duration)
                subtitle_option = await Utilities.fix_subtitle_codec(self.file_link)
                log.info(
                    "Generating sample video (duration %ss from %s) from location: %s for %s",
                    sample_duration,
                    start_at,
                    self.file_link,
                    self.chat_id,
                )
                ffmpeg_cmd = [
                    "ffmpeg",
                    "-headers",
                    f"IAM:{Config.IAM_HEADER}",
                    "-hide_banner",
                    "-ss",
                    str(start_at),
                    "-i",
                    self.file_link,
                    "-t",
                    str(sample_duration),
                    "-map",
                    "0",
                    "-c",
                    "copy",
                    sample_file,
                ]
                for option in subtitle_option:
                    ffmpeg_cmd.insert(-1, option)

                log.debug(ffmpeg_cmd)
                output = await Utilities.run_subprocess(ffmpeg_cmd)
                log.debug(
                    "FFmpeg output\n %s \n %s", output[0].decode(), output[1].decode()
                )
                if (not os.path.exists(sample_file)) or (
                    os.path.getsize(sample_file) == 0
                ):
                    ffmpeg_output = output[0].decode() + "\n" + output[1].decode()
                    log_msg = ms.SAMPLE_VIDEO_PROCESS_FAILED_GENERATION.format(
                        file_link=self.file_link,
                        sample_duration=sample_duration,
                        ffmpeg_output=ffmpeg_output,
                    )
                    raise SampleVideoProcessFailure(
                        for_user=ms.SAMPLE_VIDEO_PROCESS_FAILED, for_admin=log_msg
                    )

                thumb = await Utilities.generate_thumbnail_file(
                    sample_file, thumbnail_folder
                )
                width, height = await Utilities.get_dimentions(sample_file)
                await self.input_message.edit_message_text(
                    text=ms.SAMPLE_VIDEO_PROCESS_SUCCESS
                )
                await upload_notify()
                await self.media_message.reply_video(
                    video=str(sample_file),
                    quote=True,
                    caption=ms.VIDEO_PROCESS_CAPTION.format(
                        duration=sample_duration,
                        start=datetime.timedelta(seconds=start_at),
                    ),
                    duration=sample_duration,
                    thumb=thumb,
                    width=width,
                    height=height,
                    supports_streaming=True,
                    progress=upload_notify,
                )

                await self.input_message.edit_message_text(
                    text=ms.PROCESS_UPLOAD_CONFIRM.format(
                        total_process_duration=datetime.timedelta(
                            seconds=int(time.time() - start_time)
                        )
                    )
                )
        except SampleVideoProcessFailure as e:
            log.error(e)
            await self.input_message.edit_message_text(text=e.for_user)
            log_msg = await self.media_message.forward(Config.LOG_CHANNEL)
            await log_msg.reply_text(
                e.for_admin,
                quote=True,
            )
