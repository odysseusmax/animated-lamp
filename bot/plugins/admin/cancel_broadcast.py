from pyrogram import Filters

from ..config import Config
from ..screenshotbot import ScreenShotBot


@ScreenShotBot.on_message(Filters.private & Filters.command("cancel_broadcast") & Filters.user(Config.AUTH_USERS))
async def cncl_broadcast_(c, m):
    if len(m.command) == 1:
        return
    
    broadcast_id = m.command[1]
    
    if not c.broadcast_ids.get(broadcast_id):
        await m.reply_text(
            f"No active broadcast with id `{broadcast_id}`.",
            True
        )
        return
    
    c.broadcast_ids.pop(broadcast_id)
    
    await m.reply_text(
        f"Broadcast will be canceled soon.",
        True
    )
