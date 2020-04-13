import os 
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
    _ = await process.communicate()
    print(_)


async def generate_screenshots(input_file_link, num=5):
    try:
        uid = str(uuid.uuid4())
        output_folder = screenshot_output_folder.joinpath(uid)
        if not output_folder.exists():
            os.makedirs(output_folder)
        
        thumbnail_template = output_folder.joinpath('screenshot-%d.png')
        ffmpeg_cmd = f"ffmpeg -i '{input_file_link}' -vf fps=1/$(echo 'scale=6;' $(ffprobe -loglevel quiet -of 'compact=nokey=1:print_section=0' -show_format_entry duration {input_file_link}) ' / {num}' | bc) -vframes {num} -qscale:v 2 {thumbnail_template}"
        await run_subprocess(ffmpeg_cmd)
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
