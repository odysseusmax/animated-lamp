from pyrogram import filters

from bot.config import Config
from bot.screenshotbot import ScreenShotBot


@ScreenShotBot.on_message(
    filters.private
    & filters.command("broadcast")
    & filters.user(Config.AUTH_USERS)
    & filters.reply
)
async def broadcast_(c, m):
    await c.start_broadcast(
        broadcast_message=m.reply_to_message, admin_id=m.from_user.id
    )
