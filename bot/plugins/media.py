import asyncio

from pyrogram import Client, Filters, InlineKeyboardMarkup, InlineKeyboardButton

from bot.utils import is_valid_file, generate_stream_link, get_duration


@Client.on_message(Filters.private & Filters.media)
async def _(c, m):
    if not is_valid_file(m):
        return
    
    file_link = await generate_stream_link(m)
    if file_link is None:
        await m.reply_text(text="😟 Sorry! I cannot help you right now, I'm having hard time processing the file.", quote=True)
        return
    
    snt = await m.reply_text("Hi there, I'm getting everything ready to process your request!", quote=True)
    
    duration = await get_duration(file_link)
    hh, mm, ss = [int(i) for i in duration.split(":")]
    seconds = hh*60*60 + mm*60 + ss
    if duration is None:
        await snt.edit_message_text("😟 Sorry! I cannot open the file.")
        return
    
    await snt.edit_message_text(
        text=f"Hi, Choose the number of screenshots you need.\n\nTotal duration: `{duration}` (`{seconds}s`)",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("📸 2", 'auto+2'),
                    InlineKeyboardButton('📸 3', 'auto+3')
                ],
                [
                    InlineKeyboardButton('📸 4', 'auto+4'),
                    InlineKeyboardButton('📸 5', 'auto+5')
                ],
                [
                    InlineKeyboardButton('📸 6', 'auto+6'),
                    InlineKeyboardButton('📸 7', 'auto+7')
                ],
                [
                    InlineKeyboardButton('📸 8', 'auto+8'),
                    InlineKeyboardButton('📸 9', 'auto+9')
                ],
                [
                    InlineKeyboardButton('📸 10', 'auto+10')
                ]
            ]
        )
    )
