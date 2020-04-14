import asyncio
import traceback

from pyrogram import Client, Filters
from pyrogram.errors import FloodWait

from config import Config
from bot import user
from bot.utils import generate_screenshots, generate_list_of_media


@Client.on_callback_query(Filters.create(lambda _, query: query.data.startswith('url')))
async def _(c, m):
    asyncio.create_task(screenshot_fn(c, m))


async def screenshot_fn(c, m):
    _, num_screenshots = m.data.split('+')
    num_screenshots = int(num_screenshots)
    media_msg = m.message.reply_to_message
    #print(media_msg)
    if media_msg.empty:
        await m.edit_message_text('Why did you delete the file 😠, Now i cannot help you 😒.')
        return
    
    try:
        file_link = media_msg.text

        while True:
            try:
                await m.edit_message_text('😀 Generating screenshots!')
                break
            except FloodWait as e:
                await asyncio.sleep(e.x)
            except:
                break
        
        screenshots = await generate_screenshots(file_link, num_screenshots)
        print(screenshots)
        if not screenshots:
            while True:
                try:
                    await m.edit_message_text('😟 Sorry! Screenshot generation failed possibly due to some infrastructure failure 😥.')
                    break
                except FloodWait as e:
                    await asyncio.sleep(e.x)
                except:
                    break
            
            l = await media_msg.forward(Config.LOG_CHANNEL)
            await l.reply_text(f'stream link : {file_link}\n\n{num_screenshots} screenshots where requested and Screen shots where not generated.', True)
            return
        if isinstance(screenshots, str):
            while True:
                try:
                    await m.edit_message_text('😟 Sorry! Screenshot generation failed possibly due to some infrastructure failure 😥.')
                    break
                except FloodWait as e:
                    await asyncio.sleep(e.x)
                except:
                    break
            
            l = await media_msg.forward(Config.LOG_CHANNEL)
            await l.reply_text(f'stream link : {file_link}\n\n{num_screenshots} screenshots where requested and some error occoured\n\n{screenshots}', True)
            return
        while True:
            try:
                await m.edit_message_text(f'🤓 You requested {num_screenshots} screenshots and {len(screenshots)} screenshots generated, Now starting to upload!')
                break
            except FloodWait as e:
                await asyncio.sleep(e.x)
            except:
                break
        list_of_media = generate_list_of_media(screenshots)
        await media_msg.reply_chat_action("upload_photo")
        await media_msg.reply_media_group(list_of_media, True)
    except:
        traceback.print_exc()
        while True:
            try:
                await m.edit_message_text('😟 Sorry! Screenshot generation failed possibly due to some infrastructure failure 😥.')
                break
            except FloodWait as e:
                await asyncio.sleep(e.x)
            except:
                break
        l = await media_msg.forward(Config.LOG_CHANNEL)
        await l.reply_text(f'{num_screenshots} screenshots where requested and some error occoured\n\n{traceback.format_exc()}', True)
