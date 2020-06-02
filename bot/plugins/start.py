from pyrogram import Filters, InlineKeyboardMarkup, InlineKeyboardButton

from ..config import Config
from ..screenshotbot import ScreenShotBot


@ScreenShotBot.on_message(Filters.private & Filters.command("start"))
async def start(c, m):
    
    if not await c.db.is_user_exist(m.chat.id):
        await c.db.add_user(m.chat.id)
        await c.send_message(
            Config.LOG_CHANNEL,
            f"New User [{m.from_user.first_name}](tg://user?id={m.chat.id}) started."
        )
    
    await m.reply_text(
        text=f"Hi there {m.from_user.first_name}.\n\nI'm Screenshot Generator Bot. I can provide screenshots from your video files with out downloading the entire file (almost instantly). For more details check /help.",
        quote=True,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton('📌  Support Group', url='https://t.me/InFoTelGroup'),
                    InlineKeyboardButton('🔖  Projects Channel', url='https://t.me/TGBotsZ')
                ],
                [
                    InlineKeyboardButton('💡  Source Code', url='https://github.com/TGExplore/Screenshot-Bot'),
                    InlineKeyboardButton('👨  Master', url='https://t.me/odbots')
                ]
            ]
        )
    )
