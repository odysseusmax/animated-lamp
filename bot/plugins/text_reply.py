from pyrogram import Client, Filters


@Client.on_message(Filters.private & Filters.reply & Filters.text)
async def _(c, m):
    print(m)
