import asyncio

from pyrogram import Client, Filters, ForceReply

from config import Config
from bot import db
from bot.utils import trim_fn


@Client.on_message(Filters.private & Filters.reply)
async def _(c, m):
    
    if not await db.is_user_exist(m.chat.id):
        await db.add_user(m.chat.id)
        await c.send_message(
            Config.LOG_CHANNEL,
            f"New User [{m.from_user.first_name}](tg://user?id={m.chat.id}) started."
        )
    
    if not m.reply_to_message.reply_markup:
        print('no reply_markup')
        return
    
    if not isinstance(m.reply_to_message.reply_markup, ForceReply):
        print('not ForceReply')
        return
    
    asyncio.create_task(trim_fn(c, m))
