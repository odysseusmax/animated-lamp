import os
import re
import uuid
import asyncio
import traceback
from pathlib import Path

from pyrogram import InputMediaPhoto

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
        
        ffmpeg_dur_cmd = f"ffmpeg -i {input_file_link}"
        output = await run_subprocess(ffmpeg_dur_cmd)
        re_duration = re.compile("Duration: (.*?)\.")
        duration = re_duration.search(output[1].decode()).groups()[0]
        seconds = reduce(lambda x,y:x*60+y,map(int,duration.split(":")))
        print(seconds)
        
        for i in range(num):
            thumbnail_template = output_folder.joinpath(f'screenshot-{i}.png')
            sec = int(i*int(seconds/num-1))
            print(sec)
            ffmpeg_cmd = f"ffmpeg -ss {sec} -i '{input_file_link}' -vframes 1 '{thumbnail_template}'"
            output = await run_subprocess(ffmpeg_cmd)
        
        screenshots = []
        for i in output_folder.iterdir():
            print(i)
            if i.match('screenshot-\d.png'):
                screenshots.append(i)
        return screenshots
    except:
        traceback.print_exc()
        return traceback.format_exc()


def generate_list_of_media(screenshots):
    return [InputMediaPhoto(str(i)) for i in screenshots]
