from pyrogram import Filters

from ..config import Config
from ..screenshotbot import ScreenShotBot
from ..utils import display_settings


@ScreenShotBot.on_message(Filters.private & Filters.command("settings"))
async def start(c, m):
    
    if not await c.db.is_user_exist(m.chat.id):
        await c.db.add_user(m.chat.id)
        await c.send_message(
            Config.LOG_CHANNEL,
            f"New User [{m.from_user.first_name}](tg://user?id={m.chat.id}) started."
        )
    await display_settings(c, m)
