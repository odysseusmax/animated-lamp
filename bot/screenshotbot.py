from collections import defaultdict
import time

from pyrogram import Client

from bot.config import Config
from bot.workers import Worker


class ScreenShotBot(Client):
    def __init__(self):
        super().__init__(
            session_name=Config.SESSION_NAME,
            bot_token=Config.BOT_TOKEN,
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            workers=20,
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
        await self.process_pool.start()
        await super().stop()
        print("Session stopped. Bye!!")
