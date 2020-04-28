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
    
    btns = [
        [
            InlineKeyboardButton("📸 2", 'scht+2'),
            InlineKeyboardButton('📸 3', 'scht+3')
        ],
        [
            InlineKeyboardButton('📸 4', 'scht+4'),
            InlineKeyboardButton('📸 5', 'scht+5')
        ],
        [
            InlineKeyboardButton('📸 6', 'scht+6'),
            InlineKeyboardButton('📸 7', 'scht+7')
        ],
        [
            InlineKeyboardButton('📸 8', 'scht+8'),
            InlineKeyboardButton('📸 9', 'scht+9')
        ],
        [
            InlineKeyboardButton('📸 10', 'scht+10')
        ]
    ]
    
    if seconds >= 600:
        btns.append([
            [InlineKeyboardButton('Generate Sample Video!', 'smpl')]
        ])
    
    await snt.edit_text(
        text=f"Hi, Choose the number of screenshots you need.\n\nTotal duration: `{duration}` (`{seconds}s`)",
        reply_markup=InlineKeyboardMarkup(btns)
    )
