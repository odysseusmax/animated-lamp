import asyncio

from pyrogram import Client, Filters, InlineKeyboardMarkup, InlineKeyboardButton

from bot.utils import is_valid_file


@Client.on_message(Filters.private & Filters.media)
async def _(c, m):
    if not is_valid_file(m):
        return
    
    await m.reply_text(
        text="Please select the number of screenshots you need",
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
            ]
        )
    )
