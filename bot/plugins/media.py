import asyncio

from pyrogram import Client, Filters, InlineKeyboardMarkup, InlineKeyboardButton

from bot.utils import is_valid_file, generate_stream_link, get_duration
from config import Config


@Client.on_message(Filters.private & Filters.media)
async def _(c, m):
    if not is_valid_file(m):
        return
    
    snt = await m.reply_text("Hi there, Please wait while I'm getting everything ready to process your request!", quote=True)
    
    file_link = await generate_stream_link(m)
    if file_link is None:
        await snt.edit_text("ðŸ˜Ÿ Sorry! I cannot help you right now, I'm having hard time processing the file.", quote=True)
        l = await m.forward(Config.LOG_CHANNEL)
        await l.reply_text(f'Could not create stream link', True)
        return
    
    duration = await get_duration(file_link)
    if duration is None:
        await snt.edit_text("ðŸ˜Ÿ Sorry! I cannot open the file.")
        l = await m.forward(Config.LOG_CHANNEL)
        await l.reply_text(f'stream link : {file_link}\n\n Could not open the file.', True)
        return
    
    hh, mm, ss = [int(i) for i in duration.split(":")]
    seconds = hh*60*60 + mm*60 + ss
    
    btns = []
    i_keyboard = []
    for i in range(10):
        c = i + 1
        i_keyboard.append(
            InlineKeyboardButton(
                f"í³¸ {c}",
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
