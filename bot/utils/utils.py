import os
import re
import uuid
import asyncio
import traceback
from pathlib import Path

from pyrogram import InputMediaPhoto

from config import Config
from bot import user


screenshot_output_folder = Path('screenshots/')


def is_valid_file(msg):
    if not msg.media:
        return False
    if msg.video:
        return True
    if (msg.document) and any(mime in msg.document.mime_type for mime in ['video', "application/octet-stream"]):
        return True
    return False


async def run_subprocess(cmd):
    process = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    return await process.communicate()
    


async def generate_screenshots(input_file_link, num=5):
    try:
        uid = str(uuid.uuid4())
        output_folder = screenshot_output_folder.joinpath(uid)
        if not output_folder.exists():
            os.makedirs(output_folder)
        
        duration = await get_duration(input_file_link)
        if duration is None:
            return "Cannot open file"
        
        hh, mm, ss = [int(i) for i in duration.split(":")]
        seconds = hh*60*60 + mm*60 + ss
        print(seconds)
        
        aws = []
        reduced_sec = seconds - int(seconds*2 / 100)
        for i in range(1, 1+num):
            sec = int(reduced_sec/num) * i
            thumbnail_template = output_folder.joinpath(f'{sec}.png')
            print(sec)
            ffmpeg_cmd = f"ffmpeg -ss {sec} -i '{input_file_link}' -vframes 1 '{thumbnail_template}'"
            aws.append(run_subprocess(ffmpeg_cmd))
        
        output = await asyncio.gather(*aws)
        aws.clear()
        
        screenshots = []
        for i in output_folder.iterdir():
            print(i)
            if i.match('*.png'):
                screenshots.append(str(i))
        screenshots.sort()
        return screenshots
    except:
        traceback.print_exc()
        return traceback.format_exc()


def generate_list_of_media(screenshots):
    return [InputMediaPhoto(str(i)) for i in screenshots]


async def generate_stream_link(media_msg):
    middle_msg = await media_msg.forward(Config.MIDDLE_MAN)
    middle_msg = await user.get_messages(Config.MIDDLE_MAN, middle_msg.message_id)
    link_req_msg = await middle_msg.forward(Config.LINK_GEN_BOT)
    await user.read_history(Config.LINK_GEN_BOT)
    await asyncio.sleep(3)
    link_msg = await user.get_history(Config.LINK_GEN_BOT, 1)
    link_msg = link_msg[0]
    if link_msg.message_id == link_req_msg.message_id:
        return None
    return link_msg.text


async def get_duration(input_file_link):
    ffmpeg_dur_cmd = f"ffmpeg -i '{input_file_link}'"
    output = await run_subprocess(ffmpeg_dur_cmd)
    #print(output[1].decode())
    duration = re.findall("Duration: (.*?)\.", output[1].decode())
    if not duration:
        return None
    return duration[0]
