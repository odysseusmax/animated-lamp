from pyrogram import Client, Filters

from config import Config
from bot import db


@Client.on_message(Filters.private &  Filters.command("status") & Filters.user(Config.AUTH_USERS))
async def _(c, m):
    
    total_users = await db.total_users_count()
    await m.reply_text(text=f"Total user {total_users}", quote=True)
