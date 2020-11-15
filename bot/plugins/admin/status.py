from pyrogram import filters as Filters

from bot.config import Config
from bot.screenshotbot import ScreenShotBot


@ScreenShotBot.on_message(Filters.private & Filters.command("status") & Filters.user(Config.AUTH_USERS))
async def sts(c, m):
    total_users = await c.db.total_users_count()
    text = f"Total user(s) till date: {total_users}\n\n"
    text += f"Active users, today: {len(c.CHAT_FLOOD)}"
    await m.reply_text(text=text, quote=True)
