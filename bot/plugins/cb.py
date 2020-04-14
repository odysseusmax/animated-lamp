import asyncio
import traceback

from pyrogram import Client, Filters
from pyrogram.errors import FloodWait

from config import Config
from bot import user
from bot.utils import generate_screenshots, generate_list_of_media, generate_stream_link


@Client.on_callback_query()
async def _(c, m):
    asyncio.create_task(screenshot_fn(c, m))


async def screenshot_fn(c, m):
    num_screenshots = int(m.data)
    media_msg = m.message.reply_to_message
    try:
        while True:
            try:
                await m.edit_message_text('Processing your request, Please wait! 😴')
                break
            except FloodWait as e:
                await asyncio.sleep(e.x)
            except:
                break
        
        file_link = await generate_stream_link(media_msg)
        if file_link is None:
            await m.edit_message_text(text="😟 Sorry! I cannot help you right now, I'm having hard time processing the file.")
            l = await media_msg.forward(Config.LOG_CHANNEL)
            await l.reply_text(f'@{Config.LINK_GEN_BOT} did not respond with stream url in 5 sec.', True)
            return
            
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
