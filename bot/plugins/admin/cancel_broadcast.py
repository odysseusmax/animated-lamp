from pyrogram import filters as Filters

from bot.config import Config
from bot.screenshotbot import ScreenShotBot


@ScreenShotBot.on_callback_query(Filters.create(lambda _, __, query: query.data.startswith('cncl_bdct')) 
                                 & Filters.user(Config.AUTH_USERS))
async def cncl_broadcast_(c, cb):
    
    _, broadcast_id = cb.data.split('+')
    
    if not c.broadcast_ids.get(broadcast_id):
        await cb.answer(
            text=f"No active broadcast with id {broadcast_id}",
            show_alert=True
        )
        return
    
    c.broadcast_ids.pop(broadcast_id)
    
    await cb.answer(
        text="Broadcast will be canceled soon.",
        show_alert=True
    )
