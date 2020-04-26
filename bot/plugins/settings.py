from pyrogram import Client, Filters

from config import Config
from bot import db
from bot.utils import display_settings


@Client.on_message(Filters.private & Filters.command("settings"))
async def start(c, m):
    
    if not await db.is_user_exist(m.chat.id):
        await db.add_user(m.chat.id)
        await c.send_message(
            Config.LOG_CHANNEL,
            f"New User [{m.from_user.first_name}](tg://user?id={m.chat.id}) started."
        )
    await display_settings(m)
