import traceback
import io

from pyrogram import filters as Filters

from bot.config import Config
from bot.screenshotbot import ScreenShotBot



@ScreenShotBot.on_message(Filters.private & Filters.command("banned_users") & Filters.user(Config.AUTH_USERS))
async def _banned_usrs(c, m):
    all_banned_users = await c.db.get_all_banned_users()
    banned_usr_count = 0
    text = ''
    async for banned_user in all_banned_users:
        user_id = banned_user['id']
        ban_duration = banned_user['ban_status']['ban_duration']
        banned_on = banned_user['ban_status']['banned_on']
        ban_reason = banned_user['ban_status']['ban_reason']
        banned_usr_count += 1
        text += f"> **user_id**: `{user_id}`, **Ban Duration**: `{ban_duration}`, **Banned on**: `{banned_on}`, **Reason**: `{ban_reason}`\n\n"
    reply_text = f"Total banned user(s): `{banned_usr_count}`\n\n{text}"
    if len(reply_text) > 4096:
        banned_usrs = io.BytesIO()
        banned_usrs.name = 'banned-users.txt'
        banned_usrs.write(reply_text.encode())
        await m.reply_document(banned_usrs, True)
        return
    await m.reply_text(reply_text, True)
