import os
import re
import uuid
import asyncio
import traceback

from pyrogram import InputMediaPhoto
from pyrogram.errors import FloodWait

from config import Config
from bot import user



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
    ffmpeg_dur_cmd = f"ffmpeg -i '{input_file_link}'"
    output = await run_subprocess(ffmpeg_dur_cmd)
    print(output[1].decode())
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
