import os
import io
import time
import math
import shutil
import asyncio
import logging
import datetime

from pyrogram.types import InputMediaPhoto

from bot.config import Config
from bot.utils import Utilities
from bot.messages import Messages as ms
from bot.database import Database
from .base import BaseProcess


log = logging.getLogger(__name__)
db = Database()


class ManualScreenshotsProcessFailure(Exception):
    def __init__(self, for_user, for_admin, extra_details=None):
        self.for_user = for_user
        self.for_admin = for_admin
        self.extra_details = extra_details


class ManualScreenshotsProcess(BaseProcess):
    def __init__(self, client, input_message, reply_message):
        super().__init__(client, input_message)
        self.reply_message = reply_message

    async def _get_media_message(self):
        message = await self.client.get_messages(
            self.chat_id, self.input_message.reply_to_message.message_id
        )
        await self.input_message.reply_to_message.delete()
        return message.reply_to_message

    async def process(self):
        output_folder = Config.SCREENSHOTS_FOLDER.joinpath(self.process_id)
        os.makedirs(output_folder, exist_ok=True)
        await self.reply_message.edit_text(ms.PROCESSING_REQUEST, quote=True)
        try:
            if self.media_msg.empty:
                raise ManualScreenshotsProcessFailure(
                    for_user=ms.MEDIA_MESSAGE_DELETED,
                    for_admin=ms.MEDIA_MESSAGE_DELETED,
                )

            try:
                raw_user_input = [
                    int(i.strip()) for i in self.input_message.text.split(",")
                ]
            except Exception:
                raise ManualScreenshotsProcessFailure(
                    for_user=ms.WRONG_FORMAT,
                    for_admin=ms.WRONG_FORMAT,
                )

            await self.track_user_activity()
            start_time = time.time()

            duration = await Utilities.get_duration(self.file_link)
            if isinstance(duration, str):
                raise ManualScreenshotsProcessFailure(
                    for_user=ms.CANNOT_OPEN_FILE,
                    for_admin=ms.MANUAL_SCREENSHOTS_OPEN_ERROR.format(
                        file_link=self.file_link, duration=duration
                    ),
                )

            valid_positions = []
            invalid_positions = []
            for pos in raw_user_input:
                if 0 < pos < duration:
                    invalid_positions.append(str(pos))
                else:
                    valid_positions.append(pos)

            if not valid_positions:
                raise ManualScreenshotsProcessFailure(
                    for_user=ms.MANUAL_SCREENSHOTS_NO_VALID_POSITIONS,
                    for_admin=ms.MANUAL_SCREENSHOTS_NO_VALID_POSITIONS,
                )

            if len(valid_positions) > 10:
                raise ManualScreenshotsProcessFailure(
                    for_user=ms.MANUAL_SCREENSHOTS_VALID_PISITIONS_ABOVE_LIMIT.format(
                        valid_positions_count=len(valid_positions)
                    ),
                    for_admin=ms.MANUAL_SCREENSHOTS_VALID_PISITIONS_ABOVE_LIMIT.format(
                        valid_positions_count=len(valid_positions)
                    ),
                )

            if invalid_positions:
                txt = ms.MANUAL_SCREENSHOTS_INVALID_POSITIONS_ALERT.format(
                    invalid_positions_count=len(invalid_positions),
                    invalid_positions=", ".join(invalid_positions),
                )
            else:
                txt = ms.SCREENSHOTS_START

            await self.reply_message.edit_text(txt)
            screenshots = []
            ffmpeg_errors = ""
            as_file = await db.is_as_file(self.chat_id)
            watermark = await db.get_watermark_text(self.chat_id)
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

            log.info(
                "Generating screenshots at positions %s from location: %s for %s",
                valid_positions,
                self.file_link,
                self.chat_id,
            )

            for i, sec in enumerate(valid_positions):
                thumbnail_template = output_folder.joinpath(f"{i+1}.png")
                ffmpeg_cmd[5] = str(sec)
                ffmpeg_cmd[-1] = str(thumbnail_template)
                log.debug(ffmpeg_cmd)
                output = await Utilities.run_subprocess(ffmpeg_cmd)
                log.debug(output)
                await self.reply_message.edit_text(
                    ms.SCREENSHOTS_PROGRESS.format(
                        current=i + 1, total=len(valid_positions)
                    )
                )
                if thumbnail_template.exists():
                    if as_file:
                        screenshots.append(
                            {
                                "document": str(thumbnail_template),
                                "caption": ms.SCREENSHOT_AT.format(
                                    time=datetime.timedelta(seconds=sec)
                                ),
                            }
                        )
                    else:
                        screenshots.append(
                            InputMediaPhoto(
                                str(thumbnail_template),
                                caption=ms.SCREENSHOT_AT.format(
                                    time=datetime.timedelta(seconds=sec)
                                ),
                            )
                        )
                    continue

                ffmpeg_errors += output[0].decode() + "\n" + output[1].decode() + "\n\n"

            if not screenshots:
                error_file = None
                if ffmpeg_errors:
                    error_file = io.BytesIO()
                    error_file.name = f"{self.process_id}-errors.txt"
                    error_file.write(ffmpeg_errors.encode())
                raise ManualScreenshotsProcessFailure(
                    for_user=ms.SCREENSHOT_PROCESS_FAILED,
                    for_admin=ms.MANUAL_SCREENSHOTS_FAILED_GENERATION.format(
                        file_link=self.file_link, raw_user_input=raw_user_input
                    ),
                    extra_details=error_file,
                )

            await self.reply_message.edit_text(
                text=ms.SCREENSHOT_PROCESS_SUCCESS.format(
                    count=len(valid_positions), total_count=len(screenshots)
                )
            )
            await self.media_msg.reply_chat_action("upload_photo")
            if as_file:
                aws = [
                    self.media_msg.reply_document(quote=True, **photo)
                    for photo in screenshots
                ]
                await asyncio.gather(*aws)
            else:
                await self.media_msg.reply_media_group(screenshots, True)

            await self.reply_message.edit_text(
                ms.PROCESS_UPLOAD_CONFIRM.format(
                    total_process_duration=datetime.timedelta(
                        seconds=int(time.time() - start_time)
                    )
                )
            )
        except ManualScreenshotsProcessFailure as e:
            log.error(e)
            await self.reply_message.edit_text(e.for_user)
            log_msg = await self.media_msg.forward(Config.LOG_CHANNEL)
            if e.extra_details:
                await log_msg.reply_document(
                    document=e.extra_details, quote=True, caption=e.for_admin
                )
            else:
                await log_msg.reply_text(
                    text=e.for_admin,
                    quote=True,
                )
        finally:
            shutil.rmtree(output_folder, ignore_errors=True)
