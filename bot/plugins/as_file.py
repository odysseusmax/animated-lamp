from pyrogram import Client, Filters, InlineKeyboardMarkup, InlineKeyboardButton
from bot import db


@Client.on_callback_query(Filters.create(lambda _, query: query.data.startswith('as_file')))
async def _(c, m):
    _, as_file = m.data.split('+')
    as_file = int(as_file)
    if as_file == 1:
        await db.update_as_file(m.from_user.id, True)
    else:
        await db.update_as_file(m.from_user.id, False)
    
    as_file = await db.is_as_file(m.from_user.id)
    upload_mode_btn = [InlineKeyboardButton("🖼️ Uploading as Image.", 'as_file+0')] if as_file else [InlineKeyboardButton("📁 Uploading as Document.", 'as_file+1')]
    
    await m.edit_message_reply_markup(
        InlineKeyboardMarkup(
            [
                upload_mode_btn
            ]
        )
    )
