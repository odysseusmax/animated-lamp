import datetime

from pyrogram import filters as  Filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from ..utils import Utilities
from ..screenshotbot import ScreenShotBot
from ..config import Config


@ScreenShotBot.on_message(Filters.private & ((Filters.text & ~Filters.edited) | Filters.media) & Filters.incoming)
async def _(c, m):

    if m.media:
        if not Utilities.is_valid_file(m):
            return
    else:
        if not Utilities.is_url(m.text):
            return

    snt = await m.reply_text("Hi there, Please wait while I'm getting everything ready to process your request!", quote=True)

    if m.media:
        file_link = Utilities.generate_stream_link(m)
    else:
        file_link = m.text

    duration = await Utilities.get_duration(file_link)
    if isinstance(duration, str):
        await snt.edit_text("😟 Sorry! I cannot open the file.")
        l = await m.forward(Config.LOG_CHANNEL)
        await l.reply_text(duration, True)
        return

    btns = Utilities.gen_ik_buttons()

    if duration >= 600:
        btns.append([InlineKeyboardButton('Generate Sample Video!', 'smpl')])

    await snt.edit_text(
        text=f"Choose one of the options.\n\nTotal duration: `{datetime.timedelta(seconds=duration)}` (`{duration}s`)",
        reply_markup=InlineKeyboardMarkup(btns)
    )
