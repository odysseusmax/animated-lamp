import os
import re
import uuid
import shlex
import asyncio
import traceback

from pyrogram import InputMediaPhoto, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait

from config import Config
from bot import user, db



def is_valid_file(msg):
    if not msg.media:
        return False
    if msg.video:
        return True
    if (msg.document) and any(mime in msg.document.mime_type for mime in ['video', "application/octet-stream"]):
        return True
    return False

def is_url(text):
    url = re.findall(
        r"(http[s]*://.+)",
        text
    )
    if url:
        return True
    return False


async def run_subprocess(cmd):
    process = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    return await process.communicate()
    


async def generate_stream_link(media_msg):
    middle_msg = await media_msg.forward(Config.MIDDLE_MAN)
    middle_msg = await user.get_messages(Config.MIDDLE_MAN, middle_msg.message_id)
    link_req_msg = await middle_msg.forward(Config.LINK_GEN_BOT)
    await user.read_history(Config.LINK_GEN_BOT)
    await asyncio.sleep(2)
    link_msg = None
    async for mes in user.iter_history(Config.LINK_GEN_BOT, limit=10):
        if mes.reply_to_message and mes.reply_to_message.message_id == link_req_msg.message_id:
            link_msg = mes
    if link_msg is None:
        return None
    return link_msg.text


async def get_duration(input_file_link):
    ffmpeg_dur_cmd = f"ffmpeg -i {shlex.quote(input_file_link)}"
    #print(ffmpeg_dur_cmd)
    output = await run_subprocess(ffmpeg_dur_cmd)
    #print(output[1].decode())
    duration = re.findall("Duration: (.*?)\.", output[1].decode())
    if not duration:
        return None
    return duration[0]


async def edit_message_text(m, **kwargs):
    while True:
        try:
            return await m.edit_message_text(**kwargs)
        except FloodWait as e:
            await asyncio.sleep(e.x)
        except:
            break


async def display_settings(m, cb=False):
    chat_id = m.from_user.id if cb else m.chat.id
    
    as_file = await db.is_as_file(chat_id)
    watermark_text = await db.get_watermark_text(chat_id)
    
    
    if as_file:
        as_file_btn = [InlineKeyboardButton("Upload Mode", 'rj'), InlineKeyboardButton("📁 Uploading as Document.", 'set+af+0')]
    else:
        as_file_btn = [InlineKeyboardButton("Upload Mode", 'rj'), InlineKeyboardButton("🖼️ Uploading as Image.", 'set+af+1')]
    
    if watermark_text:
        wm_btn = [InlineKeyboardButton("Watermark", 'rj'), InlineKeyboardButton(f"{watermark_text}", 'set+wm+0')]
    else:
        wm_btn = [InlineKeyboardButton("Watermark", 'rj'), InlineKeyboardButton("No watermark exists!", 'set+wm+1')]
    
    settings_btn = [as_file_btn, wm_btn]
    
    if cb:
        await m.edit_message_reply_markup(
            InlineKeyboardMarkup(settings_btn)
        )
        return
    
    await m.reply_text(
        text = f"Here You can configure the bot's behavior.",
        quote=True,
        reply_markup=InlineKeyboardMarkup(settings_btn)
    )
