import asyncio
import traceback

from pyrogram import Client, Filters

from config import Config
from bot import user
from bot.utils import generate_screenshots, generate_list_of_media


@Client.on_callback_query()
async def _(c, m):
    asyncio.create_task(screenshot_fn(c, m))


async def screenshot_fn(c, m):
    num_screenshots = int(m.data)
    media_msg = m.message.reply_to_message
    try:
        await m.edit_message_text('Processing your request, Please wait! 😴')
        middle_msg = await media_msg.forward(Config.MIDDLE_MAN)
        middle_msg = await user.get_messages(Config.MIDDLE_MAN, middle_msg.message_id)
        link_req_msg = await middle_msg.forward(Config.LINK_GEN_BOT)
        await user.read_history(Config.LINK_GEN_BOT)
        #await middle_msg.delete()
        await asyncio.sleep(5)
        link_msg = await user.get_history(Config.LINK_GEN_BOT, 1)
        link_msg = link_msg[0]
        if link_msg.message_id == link_req_msg.message_id:
            await m.edit_message_text('😟 Sorry! Screenshot generation not possible right now due to some infrastructure failure 😥.')
            l = await media_msg.forward(Config.LOG_CHANNEL)
            await l.reply_text(f'@{Config.LINK_GEN_BOT} did not respond with stream url in 5 sec.', True)
            return
        await m.edit_message_text('😀 Generating screenshots!')
        file_link = link_msg.text
        screenshots = await generate_screenshots(file_link, num_screenshots)
        print(screenshots)
        if not screenshots:
            await m.edit_message_text('😟 Sorry! Screenshot generation failed possibly due to some infrastructure failure 😥.')
            l = await media_msg.forward(Config.LOG_CHANNEL)
            await l.reply_text(f'stream link : {file_link}\n\n{num_screenshots} screenshots where requested and Screen shots where not generated.', True)
            return
        if isinstance(screenshots, str):
            await m.edit_message_text('😟 Sorry! Screenshot generation failed possibly due to some infrastructure failure 😥.')
            l = await media_msg.forward(Config.LOG_CHANNEL)
            await l.reply_text(f'stream link : {file_link}\n\n{num_screenshots} screenshots where requested and some error occoured\n\n{screenshots}', True)
            return
        await m.edit_message_text(f'🤓 {len(screenshots)} screenshots generated, Now starting to upload!')
        list_of_media = generate_list_of_media(screenshots)
        await media_msg.reply_chat_action("upload_photo")
        await media_msg.reply_media_group(list_of_media)
    except:
        traceback.print_exc()
        await m.edit_message_text('😟 Sorry! Screenshot generation failed possibly due to some infrastructure failure 😥.')
        l = await media_msg.forward(Config.LOG_CHANNEL)
        await l.reply_text(f'{num_screenshots} screenshots where requested and some error occoured\n\n{traceback.format_exc()}', True)
