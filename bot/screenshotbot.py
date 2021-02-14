from collections import defaultdict
import logging
import time
import string
import random
import asyncio
from contextlib import contextmanager

from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.config import Config
from bot.workers import Worker
from bot.utils.broadcast import Broadcast


log = logging.getLogger(__name__)


class ScreenShotBot(Client):
    def __init__(self):
        super().__init__(
            session_name=Config.SESSION_NAME,
            bot_token=Config.BOT_TOKEN,
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            plugins=dict(root="bot/plugins"),
        )
        self.process_pool = Worker()
        self.CHAT_FLOOD = defaultdict(
            lambda: int(time.time()) - Config.SLOW_SPEED_DELAY - 1
        )
        self.broadcast_ids = {}

    async def start(self):
        await super().start()
        await self.process_pool.start()
        me = await self.get_me()
        print(f"New session started for {me.first_name}({me.username})")

    async def stop(self):
        await self.process_pool.stop()
        await super().stop()
        print("Session stopped. Bye!!")

    @contextmanager
    def track_broadcast(self, handler):
        broadcast_id = ""
        while True:
            broadcast_id = "".join(
                random.choice(string.ascii_letters) for _ in range(3)
            )
            if broadcast_id not in self.broadcast_ids:
                break

        self.broadcast_ids[broadcast_id] = handler
        try:
            yield broadcast_id
        finally:
            self.broadcast_ids.pop(broadcast_id)

    async def start_broadcast(self, broadcast_message, admin_id):
        asyncio.create_task(self._start_broadcast(broadcast_message, admin_id))

    async def _start_broadcast(self, broadcast_message, admin_id):
        try:
            broadcast_handler = Broadcast(
                client=self, broadcast_message=broadcast_message
            )
            with self.track_broadcast(broadcast_handler) as broadcast_id:
                reply_message = await self.send_message(
                    chat_id=admin_id,
                    text="Broadcast started. Use the buttons to check the progress or to cancel the broadcast.",
                    reply_to_message_id=broadcast_message.message_id,
                    reply_markup=InlineKeyboardMarkup(
                        [
                            InlineKeyboardButton(
                                text="Check Progress",
                                callback_data=f"sts_bdct+{broadcast_id}",
                            ),
                            InlineKeyboardButton(
                                text="Cancel!",
                                callback_data=f"cncl_bdct+{broadcast_id}",
                            ),
                        ]
                    ),
                )

                await broadcast_handler.start()

                await reply_message.edit_text("Broadcast completed")
        except Exception as e:
            log.error(e, exc_info=True)
