from pyrogram import Client, Filters, InlineKeyboardMarkup, InlineKeyboardButton

from config import Config
from bot import db


@Client.on_message(Filters.private & Filters.command("help"))
async def help(c, m):
    
    await m.reply_text(
        text=f"""Hi **{m.from_user.first_name}.** Welcome to Screenshot Generator Bot.
        
**My main Commands are**,
/start - Command to start bot or check whether bot is alive.
/settings - Command to configure bot's behavior
/set_watermark - Command to add custom watermark text to screenshots.
   Example: `/set_watermark watermark text`""",
        quote=True,
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton('📨  More Functions', url='https://telegra.ph/Features-of-Screenshot-Bot-05-06')]
            ]
        )
    )
