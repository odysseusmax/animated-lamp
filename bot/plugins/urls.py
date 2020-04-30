import asyncio

from pyrogram import Client, Filters, InlineKeyboardMarkup, InlineKeyboardButton

from bot.utils import is_url, get_duration
from config import Config


@Client.on_message(Filters.private & Filters.text & Filters.incoming & ~Filters.edited)
async def _(c, m):
    if not is_url(m.text):
        return

    snt = await m.reply_text("Hi there, Please wait while I'm getting everything ready to process your request!", quote=True)

    duration = await get_duration(m.text)
    if duration is None:
        await snt.edit_text("😟 Sorry! I cannot open the file.")
        l = await m.forward(Config.LOG_CHANNEL)
        await l.reply_text(f' Could not open the file.', True)
        return

    hh, mm, ss = [int(i) for i in duration.split(":")]
    seconds = hh*60*60 + mm*60 + ss

    btns = []
    i_keyboard = []
    for i in range(10):
        c = i + 1
        i_keyboard.append(
            InlineKeyboardButton(
                f"📸 {c}",
                f"scht+{c}"
        )
        if (i % 2) == 1:
            if len(i_keyboard) > 0:
                btns.append(i_keyboard)
                i_keyboard = []
    
    if seconds >= 600:
        btns.append([InlineKeyboardButton('Generate Sample Video!', 'smpl')])
    
    await snt.edit_text(
        text=f"Hi, Choose the number of screenshots you need.\n\nTotal duration: `{duration}` (`{seconds}s`)",
        reply_markup=InlineKeyboardMarkup(btns)
    )
