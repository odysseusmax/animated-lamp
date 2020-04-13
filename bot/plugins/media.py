import asyncio
import traceback

from pyrogram import Client, Filters

from config import Config
from bot import user
from bot.utils import is_valid_file, generate_screenshots, generate_list_of_media


@Client.on_message(Filters.private & Filters.media)
async def _(c, m):
    if not is_valid_file(m):
        return
    
    asyncio.create_task(screenshot_fn(c, m))


async def screenshot_fn(c, m):
    try:
        snt = await m.reply_text('processing...')
        middle_msg = await m.forward(Config.MIDDLE_MAN)
        middle_msg = await user.get_messages(Config.MIDDLE_MAN, middle_msg.message_id)
        link_req_msg = await middle_msg.forward(Config.LINK_GEN_BOT)
        await user.read_history(Config.LINK_GEN_BOT)
        await middle_msg.delete()
        await asyncio.sleep(5)
        link_msg = await user.get_history(Config.LINK_GEN_BOT, 1)
        link_msg = link_msg[0]
        if link_msg.message_id == link_req_msg.message_id:
            await snt.edit_text('Service Down!')
            return
        
        file_link = link_msg.text
        screenshots = await generate_screenshots(file_link)
        print(screenshots)
        if not screenshots:
            await snt.edit_text('Service Down!')
            return
        if isinstance(screenshots, str):
            await snt.edit_text('Service Down!')
            return
        
        list_of_media = generate_list_of_media(screenshots)
        await m.reply_media_group(list_of_media)
    except:
        traceback.print_exc()
        await snt.edit_text('Service Down!')
