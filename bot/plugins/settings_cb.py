from pyrogram import Client, Filters

from bot import db
from bot.utils import display_settings


@Client.on_callback_query(Filters.create(lambda _, query: query.data.startswith('set')))
async def _(c, m):
    _, typ, action = m.data.split('+')
    
    if typ == 'af':
        if int(action) == 0:
            await db.update_as_file(m.from_user.id, False)
            alert_text = 'From now on I\'ll upload as image files'
        else:
            await db.update_as_file(m.from_user.id, True)
            alert_text = 'From now on I\'ll upload as document files'
    
    elif typ == 'wm':
        if int(action) == 0:
            await db.update_watermark_text(m.from_user.id)
            alert_text = 'Successfully removed watermark text'
        else:
            alert_text = 'Use /set_watermark to add new watermark text.'
    
    await m.answer(alert_text, show_alert=True)

    await display_settings(m, cb=True)
    


@Client.on_callback_query(Filters.create(lambda _, query: query.data.startswith('rj')))
async def _(c, m):
    await m.answer('😂')
