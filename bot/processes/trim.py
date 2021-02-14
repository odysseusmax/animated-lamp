import os
import time
import tempfile
import logging
import datetime

from bot.config import Config
from bot.utils import Utilities
from bot.messages import Messages as ms
from .exception import BaseException
from .base import BaseProcess


log = logging.getLogger(__name__)


class TrimVideoProcessFailure(BaseException):
    pass


class TrimVideoProcess(BaseProcess):
    def __init__(self, client, input_message, reply_message):
        super().__init__(client, input_message)
        self.reply_message = reply_message

    async def cancelled(self):
        await self.reply_message.edit_text(ms.PROCESS_TIMEOUT)

    async def set_media_message(self):
        message = await self.client.get_messages(
            self.chat_id, self.input_message.reply_to_message.message_id
        )
        await self.input_message.reply_to_message.delete()
        self.media_message = message.reply_to_message

    async def process(self):
        async def upload_notify(*args):
            await self.client.send_chat_action(self.chat_id, "upload_video")

        await self.set_media_message()
        await self.reply_message.edit_text(ms.PROCESSING_REQUEST)
        try:
            if self.media_message.empty:
                raise TrimVideoProcessFailure(
                    for_user=ms.MEDIA_MESSAGE_DELETED,
                    for_admin=ms.MEDIA_MESSAGE_DELETED,
                )

            try:
                start, end = [int(i) for i in self.input_message.text.split(":")]
            except Exception:
                raise TrimVideoProcessFailure(
                    for_user=ms.WRONG_FORMAT,
                    for_admin=ms.WRONG_FORMAT,
                )

            if 0 > start > end:
                raise TrimVideoProcessFailure(
                    for_user=ms.TRIM_VIDEO_INVALID_RANGE,
                    for_admin=ms.TRIM_VIDEO_INVALID_RANGE,
                )

            request_duration = end - start
            if request_duration > Config.MAX_TRIM_DURATION:
                raise TrimVideoProcessFailure(
                    for_user=ms.TRIM_VIDEO_DURATION_ERROR.format(
                        max_duration=Config.MAX_TRIM_DURATION,
                        start=start,
                        end=end,
                        request_duration=request_duration,
                    ),
                    for_admin=ms.TRIM_VIDEO_INVALID_RANGE,
                )

            await self.track_user_activity()
            start_time = time.time()
            await self.reply_message.edit_text(ms.TRIM_VIDEO_START)

            duration = await Utilities.get_duration(self.file_link)
            if isinstance(duration, str):
                raise TrimVideoProcessFailure(
                    for_user=ms.CANNOT_OPEN_FILE,
                    for_admin=ms.TRIM_VIDEO_OPEN_ERROR.format(
                        file_link=self.file_link,
                        start=start,
                        end=end,
                        duration=duration,
                    ),
                )

            if (start >= duration) or (end >= duration):
                raise TrimVideoProcessFailure(
                    for_user=ms.TRIM_VIDEO_RANGE_OUT_OF_VIDEO_DURATION,
                    for_admin=ms.TRIM_VIDEO_RANGE_OUT_OF_VIDEO_DURATION,
                )

            log.info(
                "Trimming video (duration %ss from %s) from location: %s for %s",
                request_duration,
                start,
                self.file_link,
                self.chat_id,
            )

            temp_output_folder = tempfile.TemporaryDirectory()
            temp_thumbnail_folder = tempfile.TemporaryDirectory()
            with temp_output_folder as output_folder, temp_thumbnail_folder as thumbnail_folder:
                trim_video_file = os.path.join(output_folder, "trim_video.mkv")
                subtitle_option = await Utilities.fix_subtitle_codec(self.file_link)

                ffmpeg_cmd = [
                    "ffmpeg",
                    "-headers",
                    f"IAM:{Config.IAM_HEADER}",
                    "-hide_banner",
                    "-ss",
                    str(start),
                    "-i",
                    self.file_link,
                    "-t",
                    str(request_duration),
                    "-map",
                    "0",
                    "-c",
                    "copy",
                    trim_video_file,
                ]
                for option in subtitle_option:
                    ffmpeg_cmd.insert(-1, option)

                log.debug(ffmpeg_cmd)
                output = await Utilities.run_subprocess(ffmpeg_cmd)
                log.debug(
                    "FFmpeg output\n %s \n %s", output[0].decode(), output[1].decode()
                )

                if (not os.path.exists(trim_video_file)) or (
                    os.path.getsize(trim_video_file) == 0
                ):
                    ffmpeg_output = output[0].decode() + "\n" + output[1].decode()
                    raise TrimVideoProcessFailure(
                        for_user=ms.TRIM_VIDEO_PROCESS_FAILED,
                        for_admin=ms.TRIM_VIDEO_PROCESS_FAILED_GENERATION.format(
                            file_link=self.file_link,
                            start=start,
                            end=end,
                            ffmpeg_output=ffmpeg_output,
                        ),
                    )

                thumb = await Utilities.generate_thumbnail_file(
                    trim_video_file, thumbnail_folder
                )
                width, height = await Utilities.get_dimentions(trim_video_file)
                await self.reply_message.edit_text(ms.TRIM_VIDEO_PROCESS_SUCCESS)
                await upload_notify()
                await self.media_message.reply_video(
                    video=str(trim_video_file),
                    quote=True,
                    caption=ms.VIDEO_PROCESS_CAPTION.format(
                        duration=request_duration,
                        start=datetime.timedelta(seconds=start),
                    ),
                    duration=request_duration,
                    width=width,
                    height=height,
                    thumb=thumb,
                    supports_streaming=True,
                    progress=upload_notify,
                )

                await self.reply_message.edit_text(
                    ms.PROCESS_UPLOAD_CONFIRM.format(
                        total_process_duration=datetime.timedelta(
                            seconds=int(time.time() - start_time)
                        )
                    )
                )
        except TrimVideoProcessFailure as e:
            log.error(e)
            await self.reply_message.edit_text(text=e.for_user)
            log_msg = await self.media_message.forward(Config.LOG_CHANNEL)
            await log_msg.reply_text(
                e.for_admin,
                quote=True,
            )
