from pyrogram import Client, Filters

from bot import db
from bot.utils import display_settings
from config import Config


@Client.on_callback_query(Filters.create(lambda _, query: query.data.startswith('set')))
async def settings_cb(c, m):
    _, typ, action = m.data.split('+')
    chat_id = m.from_user.id
    
    if typ == 'af':
        if int(action) == 0:
            await db.update_as_file(chat_id, False)
            alert_text = 'From now on I\'ll upload as image files'
        else:
            await db.update_as_file(chat_id, True)
            alert_text = 'From now on I\'ll upload as document files'
    
    elif typ == 'wm':
        if int(action) == 0:
            await db.update_watermark_text(chat_id)
            alert_text = 'Successfully removed watermark text'
        else:
            alert_text = 'Use /set_watermark to add new watermark text.'
    
    elif typ == 'sv':
        sample_duration = await db.get_sample_duration(chat_id)
        if sample_duration+30 >=180:
            sample_duration = 0
        sample_duration += 30
        await db.update_sample_duration(chat_id, sample_duration)
        alert_text = f'Sample video duration changed to {sample_duration}s'
    elif typ == 'wc':
        watermark_color_code = await db.get_watermark_color(chat_id)
        if watermark_color_code+1 == len(Config.COLORS):
            watermark_color_code = -1
        watermark_color_code += 1
        await db.update_watermark_color(chat_id, watermark_color_code)
        alert_text = f'Successfully changed watermark text color to {Config.COLORS[watermark_color_code]}'
    
    await m.answer(alert_text, show_alert=True)

    await display_settings(m, cb=True)
    


@Client.on_callback_query(Filters.create(lambda _, query: query.data.startswith('rj')))
async def _(c, m):
    await m.answer('😂')
