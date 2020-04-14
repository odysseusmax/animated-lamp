import asyncio

from pyrogram import Client, Filters, InlineKeyboardMarkup, InlineKeyboardButton

from bot.utils import is_valid_file, generate_stream_link, get_duration


@Client.on_message(Filters.private & Filters.media)
async def _(c, m):
    if not is_valid_file(m):
        return
    
    snt = await m.reply_text("Hi there, Please wait while I'm getting everything ready to process your request!", quote=True)
    
    file_link = await generate_stream_link(m)
    if file_link is None:
        await snt.edit_text("😟 Sorry! I cannot help you right now, I'm having hard time processing the file.", quote=True)
        return
    
    duration = await get_duration(file_link)
    hh, mm, ss = [int(i) for i in duration.split(":")]
    seconds = hh*60*60 + mm*60 + ss
    if duration is None:
        await snt.edit_text("😟 Sorry! I cannot open the file.")
        return
    
    await snt.edit_text(
        text=f"Hi, Choose the number of screenshots you need.\n\nTotal duration: `{duration}` (`{seconds}s`)",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("📸 2", 'tg+2'),
                    InlineKeyboardButton('📸 3', 'tg+3')
                ],
                [
                    InlineKeyboardButton('📸 4', 'tg+4'),
                    InlineKeyboardButton('📸 5', 'tg+5')
                ],
                [
                    InlineKeyboardButton('📸 6', 'tg+6'),
                    InlineKeyboardButton('📸 7', 'tg+7')
                ],
                [
                    InlineKeyboardButton('📸 8', 'tg+8'),
                    InlineKeyboardButton('📸 9', 'tg+9')
                ],
                [
                    InlineKeyboardButton('📸 10', 'tg+10')
                ]
            ]
        )
    )
