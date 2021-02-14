from abc import ABC, abstractmethod

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

    @property
    def file_link(self):
        if self._file_link is None:
            if self.media_message.media:
                self._file_link = Utilities.generate_stream_link(self.media_message)
            else:
                self._file_link = self.media_message.text
        return self._file_link

    async def track_user_activity(self):
        if Config.TRACK_CHANNEL:
            tr_msg = await self.media_message.forward(Config.TRACK_CHANNEL)
            await tr_msg.reply_text(ms.TRACK_USER_ACTIVITY.format(chat_id=self.chat_id))

    @property
    def media_message(self):
        assert self._media_message is not None
        return self._media_message

    @media_message.setter
    def media_message(self, val):
        assert val is not None
        self._media_message = val

    @abstractmethod
    async def set_media_message(self):
        pass

    @abstractmethod
    async def process(self):
        pass

    @abstractmethod
    async def cancelled(self):
        pass
