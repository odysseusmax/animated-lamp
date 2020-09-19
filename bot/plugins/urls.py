import datetime

from pyrogram import filters as  Filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from ..utils import is_url, is_valid_file, get_duration, gen_ik_buttons, generate_stream_link, get_media_info
from ..screenshotbot import ScreenShotBot
from ..config import Config


@ScreenShotBot.on_message(Filters.private & ((Filters.text & ~Filters.edited) | Filters.media) & Filters.incoming)
async def _(c, m):

    if m.media:
        if not is_valid_file(m):
            return
    else:
        if not is_url(m.text):
            return

    snt = await m.reply_text("Hi there, Please wait while I'm getting everything ready to process your request!", quote=True)

    media_info = await get_media_info(c, m.chat.id, m.message_id)
    duration = get_duration(media_info)
    if isinstance(duration, str):
        await snt.edit_text("😟 Sorry! I cannot open the file.")
        l = await m.forward(Config.LOG_CHANNEL)
        await l.reply_text(duration, True)
        return

    btns = gen_ik_buttons()

    if duration >= 600:
        btns.append([InlineKeyboardButton('Generate Sample Video!', 'smpl')])

    await snt.edit_text(
        text=f"Choose one of the options.\n\nTotal duration: `{datetime.timedelta(seconds=duration)}` (`{duration}s`)",
        reply_markup=InlineKeyboardMarkup(btns)
    )
