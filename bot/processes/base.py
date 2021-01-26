from abc import ABC, abstractmethod
from uuid import uuid4
import asyncio

from bot.config import Config
from bot.messages import Messages as ms
from bot.utils import Utilities


class BaseProcess(ABC):
    def __init__(self, client, input_message):
        self.client = client
        self.input_message = input_message
        self.chat_id = self.input_message.from_user.id

        self._file_link = None
        self._media_message = None
        self.process_id = str(uuid4())

    @property
    def file_link(self):
        if self._file_link is None:
            if self.media_msg.media:
                self._file_link = Utilities.generate_stream_link(self.media_msg)
            else:
                self._file_link = self.media_msg.text
        return self._file_link

    async def track_user_activity(self):
        if Config.TRACK_CHANNEL:
            tr_msg = await self.media_msg.forward(Config.TRACK_CHANNEL)
            await tr_msg.reply_text(ms.TRACK_USER_ACTIVITY.format(chat_id=self.chat_id))

    @property
    def media_message(self):
        if self._media_message is None:
            self._media_message = asyncio.get_running_loop().run_until_complete(self._get_media_message())
        return self._media_message

    @abstractmethod
    async def _get_media_message(self):
        pass

    @abstractmethod
    async def process(self):
        pass
