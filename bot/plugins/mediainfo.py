import io
import os
import json
import logging

from pyrogram import filters as  Filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import aiohttp

from ..screenshotbot import ScreenShotBot
from ..config import Config
from ..utils import Utilities


logger = logging.getLogger(__name__)


@ScreenShotBot.on_callback_query(Filters.create(lambda _, __, query: query.data.startswith('mi')))
async def _(c, m):
    await m.answer()
    media_msg = m.message.reply_to_message
    if media_msg.empty:
        await m.edit_message_text(text='Why did you delete the file 😠, Now i cannot help you 😒.')
        return

    await m.edit_message_text(text='Your media info will be send here shortly!')
    if media_msg.media:
        file_link = Utilities.generate_stream_link(media_msg)
    else:
        file_link = media_msg.text

    logger.info(f"Generating mediainfo from {file_link} for {m.from_user.id}")
    media_info = await Utilities.get_media_info(file_link)
    media_info_file = io.BytesIO()
    media_info_file.name = "mediainfo.json"
    media_info_file.write(media_info)
    await c.send_document(chat_id=m.from_user.id, document=media_info_file,
                          reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('Get Web URL', 'webmi')]]))


@ScreenShotBot.on_callback_query(Filters.create(lambda _, __, query: query.data.startswith('webmi')))
async def __(c, m):
    # https://github.com/eyaadh/megadlbot_oss/blob/306fb21dbdbdc8dc17294a6cb7b7cdafb11e44da/mega/helpers/media_info.py#L30
    await m.answer()
    media_info = await m.message.download()
    neko_endpoint = "https://nekobin.com/api/documents"
    async with aiohttp.ClientSession() as nekoSession:
        payload = {"content": open(media_info, 'r').read()}
        async with nekoSession.post(neko_endpoint, data=payload) as resp:
            resp = await resp.json()
            neko_link = f"https://nekobin.com/{resp['result']['key']}"
    logger.debug(neko_link)
    await m.edit_message_reply_markup(InlineKeyboardMarkup([[InlineKeyboardButton('Web URL', url=neko_link)]]))
    try:
        os.remove(media_info)
    except:
        pass
