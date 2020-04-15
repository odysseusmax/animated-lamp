import os
import uuid
import time
import asyncio
import datetime
import traceback

from pyrogram import Client, Filters, InputMediaPhoto
from pyrogram.errors import FloodWait

from config import Config
from bot import user, db
from bot.utils import get_duration, edit_message_text, run_subprocess


@Client.on_callback_query(Filters.create(lambda _, query: query.data.startswith('url')))
async def _(c, m):
    asyncio.create_task(screenshot_fn(c, m))


async def screenshot_fn(c, m):
    _, num_screenshots = m.data.split('+')
    num_screenshots = int(num_screenshots)
    media_msg = m.message.reply_to_message
    #print(media_msg)
    if media_msg.empty:
        await edit_message_text(m, text='Why did you delete the file 😠, Now i cannot help you 😒.')
        return
    
    uid = str(uuid.uuid4())
    output_folder = Config.SCRST_OP_FLDR.joinpath(uid)
    if not output_folder.exists():
        os.makedirs(output_folder)
    
    try:
        start_time = time.time()
        
        file_link = media_msg.text

        await edit_message_text(m, text='😀 Generating screenshots!')
        
        duration = await get_duration(file_link)
        if duration is None:
            await edit_message_text(m, text="😟 Sorry! I cannot open the file.")
            l = await media_msg.forward(Config.LOG_CHANNEL)
            await l.reply_text(f'stream link : {file_link}\n\n{num_screenshots} Could not open the file.', True)
            return

        hh, mm, ss = [int(i) for i in duration.split(":")]
        seconds = hh*60*60 + mm*60 + ss
        reduced_sec = seconds - int(seconds*2 / 100)
        print(f"Total seconds: {seconds}, Reduced seconds: {reduced_sec}")
        as_file = await db.is_as_file(m.from_user.id)

        screenshots = []
        for i in range(1, 1+num_screenshots):
            sec = int(reduced_sec/num_screenshots) * i
            thumbnail_template = output_folder.joinpath(f'{i}.png')
            print(sec)
            ffmpeg_cmd = f"ffmpeg -ss {sec} -i '{file_link}' -vframes 1 '{thumbnail_template}'"
            output = await run_subprocess(ffmpeg_cmd)
            await edit_message_text(m, text=f'`{i}` of `{num_screenshots}` generated!')
            if thumbnail_template.exists():
                if as_file:
                    screenshots.append({
                        'document':str(thumbnail_template),
                        'caption':f"ScreenShot at {datetime.timedelta(seconds=sec)}"
                    })
                else:
                    screenshots.append(
                        InputMediaPhoto(
                            str(thumbnail_template),
                            caption=f"ScreenShot at {datetime.timedelta(seconds=sec)}"
                        )
                    )
        
        if not screenshots:
            await edit_message_text(m, text="😟 Sorry! I cannot open the file.")
            l = await media_msg.forward(Config.LOG_CHANNEL)
            await l.reply_text(f'Could not open the file.', True)
            return
        
        await edit_message_text(m, text=f'🤓 You requested {num_screenshots} screenshots and {len(screenshots)} screenshots generated, Now starting to upload!')
        
        await media_msg.reply_chat_action("upload_photo")
        
        if as_file:
            aws = [media_msg.reply_document(quote=True, **photo) for photo in screenshots]
            await asyncio.gather(*aws)
        else:
            await media_msg.reply_media_group(screenshots, True)
        
        await edit_message_text(m, text=f'Successfully completed process in {datetime.timedelta(seconds=int(time.time()-start_time))}')
    except:
        traceback.print_exc()
        await edit_message_text(m, text='😟 Sorry! Screenshot generation failed possibly due to some infrastructure failure 😥.')
        
        l = await media_msg.forward(Config.LOG_CHANNEL)
        await l.reply_text(f'{num_screenshots} screenshots where requested and some error occoured\n\n{traceback.format_exc()}', True)
