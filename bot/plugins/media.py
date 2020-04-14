import asyncio

from pyrogram import Client, Filters, InlineKeyboardMarkup, InlineKeyboardButton

from bot.utils import is_valid_file, generate_stream_link, get_duration


@Client.on_message(Filters.private & Filters.media)
async def _(c, m):
    if not is_valid_file(m):
        return
    
    file_link = await generate_stream_link(m)
    if file_link is None:
        await m.reply_text(text="😟 Sorry! I cannot help you right now, I'm having hard time processing the file.")
        return
    
    duration = await get_duration(file_link)
    hh, mm, ss = [int(i) for i in duration.split(":")]
    seconds = hh*60*60 + mm*60 + ss
    if duration is None:
        await m.reply_text(text="😟 Sorry! I open the file.")
        return
    
    await m.reply_text(
        text=f"Hi, Choose the number of screenshots you need.\n\nTotal duration: `{duration}` (`{seconds}`)",
        quote=True,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("📸 2", '2'),
                    InlineKeyboardButton('📸 3', '3')
                ],
                [
                    InlineKeyboardButton('📸 4', '4'),
                    InlineKeyboardButton('📸 5', '5')
                ],
                [
                    InlineKeyboardButton('📸 6', '6'),
                    InlineKeyboardButton('📸 7', '7')
                ],
                [
                    InlineKeyboardButton('📸 8', '8'),
                    InlineKeyboardButton('📸 9', '9')
                ],
                [
                    InlineKeyboardButton('📸 10', '10')
                ],
                [
                    InlineKeyboardButton('🧑‍🏭 Manual Mode 🧑‍🏭', '10')
                ],
            ]
        )
    )
