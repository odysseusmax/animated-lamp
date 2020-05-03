import asyncio
import datetime

from pyrogram import Client, Filters, InlineKeyboardMarkup, InlineKeyboardButton

from bot.utils import is_url, get_duration, gen_ik_buttons
from config import Config
from bot import db


@Client.on_message(Filters.private & Filters.text & Filters.incoming & ~Filters.edited)
async def _(c, m):
    if not await db.is_user_exist(m.chat.id):
        await db.add_user(m.chat.id)
        await c.send_message(
            Config.LOG_CHANNEL,
            f"New User [{m.from_user.first_name}](tg://user?id={m.chat.id}) started."
        )
    
    if not is_url(m.text):
        return

    snt = await m.reply_text("Hi there, Please wait while I'm getting everything ready to process your request!", quote=True)

    duration = await get_duration(m.text)
    if isinstance(duration, str):
        await snt.edit_text("😟 Sorry! I cannot open the file.")
        l = await m.forward(Config.LOG_CHANNEL)
        await l.reply_text(duration, True)
        return

    btns = gen_ik_buttons()
    
    if duration >= 600:
        btns.append([InlineKeyboardButton('Generate Sample Video!', 'smpl')])
        btns.append([InlineKeyboardButton('Trim Video', 'trim')])
    
    await snt.edit_text(
        text=f"Hi, Choose the number of screenshots you need.\n\nTotal duration: `{datetime.timedelta(seconds=duration)}` (`{duration}s`)",
        reply_markup=InlineKeyboardMarkup(btns)
    )
