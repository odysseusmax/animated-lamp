from pyrogram import Client, Filters

from config import Config


@Client.on_message(Filters.private & Filters.command("start"))
async def start(c, m):
    await m.reply_text(text = f"Hi {m.from_user.first_name}.\n\nI'm Screenshot Generator Bot. I'm **Not The Only Screenshot Bot** that gives you screenshots with out downloading the entire file. Send me any telegram streamable or document video file, I'll generate the screenshots for you.", quote=True)
