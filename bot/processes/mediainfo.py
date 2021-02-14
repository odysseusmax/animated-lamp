import io
import time
import logging
import datetime

from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.config import Config
from bot.utils import Utilities
from bot.messages import Messages as ms
from .exception import BaseException
from .base import BaseProcess


log = logging.getLogger(__name__)


class MediaInfoProcessFailure(BaseException):
    pass


class MediaInfoProcess(BaseProcess):
    async def cancelled(self):
        await self.input_message.edit_message_text(ms.PROCESS_TIMEOUT)

    async def set_media_message(self):
        self.media_message = self.input_message.message.reply_to_message

    async def process(self):
        await self.set_media_message()
        await self.input_message.edit_message_text(ms.PROCESSING_REQUEST)
        try:
            if self.media_message.empty:
                raise MediaInfoProcessFailure(
                    for_user=ms.MEDIA_MESSAGE_DELETED,
                    for_admin=ms.MEDIA_MESSAGE_DELETED,
                )

            await self.track_user_activity()
            start_time = time.time()
            await self.input_message.edit_message_text(ms.MEDIAINFO_START)

            log.info(
                "Generating mediainfo from %s for %s",
                self.file_link,
                self.chat_id,
            )

            media_info = await Utilities.get_media_info(self.file_link)
            log.debug(media_info)
            media_info_file = io.BytesIO()
            media_info_file.name = "mediainfo.json"
            media_info_file.write(media_info)

            await self.media_message.reply_document(
                document=media_info_file,
                quote=True,
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("Get Web URL", callback_data="webmi")]]
                ),
            )

            await self.input_message.edit_message_text(
                ms.PROCESS_UPLOAD_CONFIRM.format(
                    total_process_duration=datetime.timedelta(
                        seconds=int(time.time() - start_time)
                    )
                )
            )
        except MediaInfoProcessFailure as e:
            log.error(e)
            await self.input_message.edit_message_text(text=e.for_user)
            log_msg = await self.media_message.forward(Config.LOG_CHANNEL)
            await log_msg.reply_text(
                e.for_admin,
                quote=True,
            )
