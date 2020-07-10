import time
import asyncio
import datetime

from pyrogram import Filters, InlineKeyboardMarkup, InlineKeyboardButton

from ..utils import is_valid_file, generate_stream_link, get_duration, gen_ik_buttons
from ..config import Config
from ..screenshotbot import ScreenShotBot


@ScreenShotBot.on_message(Filters.private & Filters.media)
async def _(c, m):
    
    chat_id = m.chat.id
    if not c.CHAT_FLOOD.get(chat_id):
        c.CHAT_FLOOD[chat_id] = int(time.time()) - Config.SLOW_SPEED_DELAY-1

    if int(time.time()) - c.CHAT_FLOOD.get(chat_id) < Config.SLOW_SPEED_DELAY:
        return
    
    c.CHAT_FLOOD[chat_id] = int(time.time())
    
    if not await c.db.is_user_exist(chat_id):
        await c.db.add_user(chat_id)
        await c.send_message(
            Config.LOG_CHANNEL,
            f"New User [{m.from_user.first_name}](tg://user?id={chat_id}) started."
        )
    
    ban_status = await c.db.get_ban_status(chat_id)
    if ban_status['is_banned']:
        if (datetime.date.today() - datetime.date.fromisoformat(ban_status['banned_on'])).days > ban_status['ban_duration']:
            await c.db.remove_ban(chat_id)
        else:
            await m.reply_text(
                f"Sorry Dear, You misused me. So you are **Blocked!**.\n\nBlock Reason: __{ban_status['ban_reason']}__",
                quote=True
            )
            return
    
    if m.document:
        if "video" not in m.document.mime_type:
            await m.reply_text(f"**😟 Sorry! Only support Media Files.**\n**Your File type :** `{m.document.mime_type}.`", quote=True)

    if not is_valid_file(m):
        return
    
    snt = await m.reply_text("Hi there, Please wait while I'm getting everything ready to process your request!", quote=True)
    
    file_link = generate_stream_link(m)
    
    duration = await get_duration(file_link)
    if isinstance(duration, str):
        await snt.edit_text("😟 Sorry! I cannot open the file.")
        l = await m.forward(Config.LOG_CHANNEL)
        await l.reply_text(f'stream link : {file_link}\n\n {duration}', True)
        return
    
    btns = gen_ik_buttons()
    
    if duration >= 600:
        btns.append([InlineKeyboardButton('Generate Sample Video!', 'smpl')])
    
    await snt.edit_text(
        text=f"Hi, Choose the number of screenshots you need.\n\nTotal duration: `{datetime.timedelta(seconds=duration)}` (`{duration}s`)",
        reply_markup=InlineKeyboardMarkup(btns)
    )
