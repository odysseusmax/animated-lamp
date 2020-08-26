from pyrogram import filters as Filters

from bot.config import Config
from bot.screenshotbot import ScreenShotBot


@ScreenShotBot.on_message(Filters.private & Filters.command("status") & Filters.user(Config.AUTH_USERS))
async def sts(c, m):
    
    total_users = await c.db.total_users_count()
    await m.reply_text(text=f"Total user(s) {total_users}", quote=True)
