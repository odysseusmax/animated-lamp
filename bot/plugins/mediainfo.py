import io
import json

from pyrogram import filters as  Filters

from ..screenshotbot import ScreenShotBot
from ..config import Config
from ..utils import get_media_info


@ScreenShotBot.on_callback_query(Filters.create(lambda _, __, query: query.data.startswith('mi')))
async def _(c, m):
    media_msg = m.message.reply_to_message
    if media_msg.empty:
        await m.edit_message_text(text='Why did you delete the file 😠, Now i cannot help you 😒.')
        return

    media_info = await get_media_info(c, m.from_user.id, media_msg.message_id)
    media_info_file = io.BytesIO()
    json.dump(media_info, media_info_file)
    await m.edit_message_text(text='Your media info will be send here shortly')
    await c.send_document(m.from_user.id, media_info_file)
