from pyrogram import filters as Filters

from bot.config import Config
from bot.screenshotbot import ScreenShotBot


@ScreenShotBot.on_message(Filters.private & Filters.command("admin") & Filters.user(Config.AUTH_USERS))
async def admin(c, m):

    text = 'Current admins of the bot:\n\n'
    admins = await c.get_users(Config.AUTH_USERS)
    for admn in admins:
        text += f'\t- {admn.mention}\n'

    text += "\nAvailable admin commands are:\n"
    text += "\t- /unban_user\n\t- /broadcast\n\t- /banned_users\n\t- /ban_user\n\t- /status"

    await m.reply_text(text, quote=True)
