from pyrogram import Client, Filters, InlineKeyboardMarkup, InlineKeyboardButton

from config import Config
from bot import db


@Client.on_message(Filters.private & Filters.command("settings"))
async def start(c, m):
    
    if not await db.is_user_exist(m.chat.id):
        await db.add_user(m.chat.id)
        await c.send_message(
            Config.LOG_CHANNEL,
            f"New User [{m.from_user.first_name}](tg://user?id={m.chat.id}) started."
        )
    as_file = await db.is_as_file(m.chat.id)
    upload_mode_btn = [InlineKeyboardButton("🖼️ Uploading as Image.", 'as_file+1')] if as_file else [InlineKeyboardButton("📁 Uploading as Document.", 'as_file+0')]
    
    await m.reply_text(
        text = f"Here You can configure the bot's behavior.",
        quote=True,
        reply_markup=InlineKeyboardMarkup(
            [
                upload_mode_btn
            ]
        )
    )
