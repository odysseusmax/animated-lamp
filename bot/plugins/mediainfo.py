import io
import json

from pyrogram import filters as  Filters

from ..screenshotbot import ScreenShotBot
from ..config import Config
from ..utils import get_media_info, generate_stream_link


@ScreenShotBot.on_callback_query(Filters.create(lambda _, __, query: query.data.startswith('mi')))
async def _(c, m):
    media_msg = m.message.reply_to_message
    if media_msg.empty:
        await m.edit_message_text(text='Why did you delete the file 😠, Now i cannot help you 😒.')
        return

    if media_msg.media:
        file_link = generate_stream_link(media_msg)
    else:
        file_link = media_msg.text

    media_info = await get_media_info(file_link)
    media_info_file = io.BytesIO()
    media_info_file.name = "mediainfo.json"
    media_info_file.write(json.dumps(media_info).encode())
    await m.edit_message_text(text='Your media info will be send here shortly!')
    await c.send_document(chat_id=m.from_user.id, document=media_info_file)
