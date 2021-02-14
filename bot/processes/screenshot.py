import os
import io
import time
import math
import logging
import tempfile
import datetime

from pyrogram.types import InputMediaPhoto, InputMediaDocument

from bot.config import Config
from bot.utils import Utilities
from bot.messages import Messages as ms
from bot.database import Database
from .base import BaseProcess
from .exception import BaseException


log = logging.getLogger(__name__)
db = Database()


class ScreenshotsProcessFailure(BaseException):
    pass


class ScreenshotsProcess(BaseProcess):
    async def set_media_message(self):
        self.media_message = self.input_message.message.reply_to_message

    async def cancelled(self):
        await self.input_message.edit_message_text(ms.PROCESS_TIMEOUT)

    async def process(self):
        await self.set_media_message()
        _, num_screenshots = self.input_message.data.split("+")
        num_screenshots = int(num_screenshots)
        await self.input_message.edit_message_text(ms.PROCESSING_REQUEST)
        try:
            if self.media_message.empty:
                raise ScreenshotsProcessFailure(
                    for_user=ms.MEDIA_MESSAGE_DELETED,
                    for_admin=ms.MEDIA_MESSAGE_DELETED,
                )

            await self.track_user_activity()
            start_time = time.time()
            await self.input_message.edit_message_text(ms.SCREENSHOTS_START)
            duration = await Utilities.get_duration(self.file_link)
            if isinstance(duration, str):
                raise ScreenshotsProcessFailure(
                    for_user=ms.CANNOT_OPEN_FILE,
                    for_admin=ms.SCREENSHOTS_OPEN_ERROR.format(
                        file_link=self.file_link,
                        num_screenshots=num_screenshots,
                        duration=duration,
                    ),
                )

            log.info(
                "Generating %s screenshots from location: %s for %s",
                num_screenshots,
                self.file_link,
                self.chat_id,
            )

            reduced_sec = duration - int(duration * 2 / 100)
            screenshots = []
            watermark = await db.get_watermark_text(self.chat_id)
            as_file = await db.is_as_file(self.chat_id)
            screenshot_mode = await db.get_screenshot_mode(self.chat_id)
            ffmpeg_errors = ""
            watermark_options = "scale=1280:-1"
            if watermark:
                watermark_color_code = await db.get_watermark_color(self.chat_id)
                watermark_color = Config.COLORS[watermark_color_code]
                watermark_position = await db.get_watermark_position(self.chat_id)
                font_size = await db.get_font_size(self.chat_id)
                width, height = await Utilities.get_dimentions(self.file_link)
                fontsize = int(
                    (math.sqrt(width ** 2 + height ** 2) / 1388.0)
                    * Config.FONT_SIZES[font_size]
                )
                x_pos, y_pos = Utilities.get_watermark_coordinates(
                    watermark_position, width, height
                )
                watermark_options = (
                    f"drawtext=fontcolor={watermark_color}:fontsize={fontsize}:x={x_pos}:"
                    f"y={y_pos}:text={watermark}, scale=1280:-1"
                )

            ffmpeg_cmd = [
                "ffmpeg",
                "-headers",
                f"IAM:{Config.IAM_HEADER}",
                "-hide_banner",
                "-ss",
                "",  # To be replaced in loop
                "-i",
                self.file_link,
                "-vf",
                watermark_options,
                "-y",
                "-vframes",
                "1",
                "",  # To be replaced in loop
            ]

            screenshot_secs = [
                int(reduced_sec / num_screenshots) * i
                if screenshot_mode == 0
                else Utilities.get_random_start_at(reduced_sec)
                for i in range(1, 1 + num_screenshots)
            ]

            with tempfile.TemporaryDirectory() as output_folder:
                for i, sec in enumerate(screenshot_secs):
                    thumbnail_file = os.path.join(output_folder, f"{i+1}.png")
                    ffmpeg_cmd[5] = str(sec)
                    ffmpeg_cmd[-1] = thumbnail_file
                    log.debug(ffmpeg_cmd)
                    output = await Utilities.run_subprocess(ffmpeg_cmd)
                    log.debug(
                        "FFmpeg output\n %s \n %s",
                        output[0].decode(),
                        output[1].decode(),
                    )
                    await self.input_message.edit_message_text(
                        ms.SCREENSHOTS_PROGRESS.format(
                            current=i + 1, total=num_screenshots
                        )
                    )
                    if os.path.exists(thumbnail_file):
                        if as_file:
                            InputMedia = InputMediaDocument
                        else:
                            InputMedia = InputMediaPhoto

                        screenshots.append(
                            InputMedia(
                                thumbnail_file,
                                caption=ms.SCREENSHOT_AT.format(
                                    time=datetime.timedelta(seconds=sec)
                                ),
                            )
                        )
                        continue

                    ffmpeg_errors += (
                        output[0].decode() + "\n" + output[1].decode() + "\n\n"
                    )

                if not screenshots:
                    error_file = None
                    if ffmpeg_errors:
                        error_file = io.BytesIO()
                        error_file.name = "errors.txt"
                        error_file.write(ffmpeg_errors.encode())
                    raise ScreenshotsProcessFailure(
                        for_user=ms.SCREENSHOT_PROCESS_FAILED,
                        for_admin=ms.SCREENSHOTS_FAILED_GENERATION.format(
                            file_link=self.file_link, num_screenshots=num_screenshots
                        ),
                        extra_details=error_file,
                    )

                await self.input_message.edit_message_text(
                    text=ms.SCREENSHOT_PROCESS_SUCCESS.format(
                        count=num_screenshots, total_count=len(screenshots)
                    )
                )
                await self.client.send_chat_action(self.chat_id, "upload_photo")
                await self.media_message.reply_media_group(screenshots, True)
                await self.input_message.edit_message_text(
                    ms.PROCESS_UPLOAD_CONFIRM.format(
                        total_process_duration=datetime.timedelta(
                            seconds=int(time.time() - start_time)
                        )
                    )
                )
        except ScreenshotsProcessFailure as e:
            log.error(e)
            await self.input_message.edit_message_text(e.for_user)
            log_msg = await self.media_message.forward(Config.LOG_CHANNEL)
            if e.extra_details:
                await log_msg.reply_document(
                    document=e.extra_details, quote=True, caption=e.for_admin
                )
            else:
                await log_msg.reply_text(
                    text=e.for_admin,
                    quote=True,
                )
