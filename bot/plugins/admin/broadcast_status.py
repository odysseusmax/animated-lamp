from pyrogram import Filters

from bot.config import Config
from bot.screenshotbot import ScreenShotBot


@ScreenShotBot.on_message(Filters.private & Filters.command("check_broadcast_status") & Filters.user(Config.AUTH_USERS))
async def sts_broadcast_(c, m):
    if len(m.command) == 1:
        return
    
    broadcast_id = m.command[1]
    
    if not c.broadcast_ids.get(broadcast_id):
        await m.reply_text(
            f"No active broadcast with id `{broadcast_id}`.",
            True
        )
        return
    
    sts_txt = ''
    for key, value in c.broadcast_ids[broadcast_id].items():
        sts_txt += f'{key} = {value}\n'
    
    await m.reply_text(
        f"Broadcast Status for `{broadcast_id}`\n\n{sts_txt}",
        True
    )
