from pyrogram import filters, Client

from bot.config import Config


@Client.on_message(filters.private & filters.command("status") & filters.user(Config.AUTH_USERS))
async def sts(c, m):
    total_users = await c.db.total_users_count()
    text = f"Total user(s) till date: {total_users}\n\n"
    text += f"Bot Updates Active Users: {len(c.CHAT_FLOOD)}"
    await m.reply_text(text=text, quote=True)
