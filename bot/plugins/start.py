from pyrogram import Client, Filters

from config import Config


@Client.on_message(Filters.private & Filters.command("start"))
async def start(c, m):
    await m.reply_text(text = "Hi there.", quote=True)
