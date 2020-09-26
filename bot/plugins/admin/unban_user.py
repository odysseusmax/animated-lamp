import logging
import traceback

from pyrogram import filters as Filters

from bot.config import Config
from bot.screenshotbot import ScreenShotBot


log = logging.getLogger(__name__)


@ScreenShotBot.on_message(Filters.private & Filters.command("unban_user") & Filters.user(Config.AUTH_USERS))
async def unban(c, m):
    if len(m.command) == 1:
        await m.reply_text(
            f"Use this command to unban any user.\n\nUsage:\n\n`/unban_user user_id`\n\nEg: `/unban_user 1234567`\n This will unban user with id `1234567`.",
            quote=True
        )
        return

    try:
        user_id = int(m.command[1])
        unban_log_text = f"Unbanning user {user_id}"

        try:
            await c.send_message(
                user_id,
                f"Your ban was lifted!"
            )
            unban_log_text += '\n\nUser notified successfully!'
        except Exception as e:
            log.debug(e, exc_info=True)
            unban_log_text += f"\n\nUser notification failed! \n\n`{traceback.format_exc()}`"
        await c.db.remove_ban(user_id)
        log.debug(unban_log_text)
        await m.reply_text(
            unban_log_text,
            quote=True
        )
    except Exception as e:
        log.error(e, exc_info=True)
        await m.reply_text(
            f"Error occoured! Traceback given below\n\n`{traceback.format_exc()}`",
            quote=True
        )
