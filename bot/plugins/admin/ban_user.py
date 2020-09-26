import logging
import traceback

from pyrogram import filters as Filters

from bot.config import Config
from bot.screenshotbot import ScreenShotBot


log = logging.getLogger(__name__)


@ScreenShotBot.on_message(Filters.private & Filters.command("ban_user") & Filters.user(Config.AUTH_USERS))
async def ban(c, m):

    if len(m.command) == 1:
        await m.reply_text(
            f"Use this command to ban any user from the bot.\n\nUsage:\n\n`/ban_user user_id ban_duration ban_reason`\n\nEg: `/ban_user 1234567 28 You misused me.`\n This will ban user with id `1234567` for `28` days for the reason `You misused me`.",
            quote=True
        )
        return

    try:
        user_id = int(m.command[1])
        ban_duration = int(m.command[2])
        ban_reason = ' '.join(m.command[3:])
        ban_log_text = f"Banning user {user_id} for {ban_duration} days for the reason {ban_reason}."

        try:
            await c.send_message(
                user_id,
                f"You are banned to use this bot for **{ban_duration}** day(s) for the reason __{ban_reason}__ \n\n**Message from the admin**"
            )
            ban_log_text += '\n\nUser notified successfully!'
        except Exception as e:
            log.debug(e, exc_info=True)
            ban_log_text += f"\n\nUser notification failed! \n\n`{traceback.format_exc()}`"
        await c.db.ban_user(user_id, ban_duration, ban_reason)
        log.debug(ban_log_text)
        await m.reply_text(
            ban_log_text,
            quote=True
        )
    except Exception as e:
        log.error(e, exc_info=True)
        await m.reply_text(
            f"Error occoured! Traceback given below\n\n`{traceback.format_exc()}`",
            quote=True
        )
