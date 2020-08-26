from pyrogram import filters as Filters

from bot.config import Config
from bot.screenshotbot import ScreenShotBot


@ScreenShotBot.on_callback_query(Filters.create(lambda _, __, query: query.data.startswith('sts_bdct')) 
                                 & Filters.user(Config.AUTH_USERS))
async def sts_broadcast_(c, cb):
    
    _, broadcast_id = cb.data.split('+')
    
    if not c.broadcast_ids.get(broadcast_id):
        await cb.answer(
            text=f"No active broadcast with id {broadcast_id}",
            show_alert=True
        )
        return
    
    sts_txt = ''
    for key, value in c.broadcast_ids[broadcast_id].items():
        sts_txt += f'{key} = {value}\n'
    
    await cb.answer(
        text=f"Broadcast Status for {broadcast_id}\n\n{sts_txt}",
        show_alert=True
    )
