from pyrogram import filters as  Filters
from pyrogram.types import ForceReply

from ..utils import Utilities
from ..screenshotbot import ScreenShotBot
from ..config import Config


@ScreenShotBot.on_message(Filters.private & Filters.reply)
async def _(c, m):

    if not m.reply_to_message.reply_markup:
        return

    if not isinstance(m.reply_to_message.reply_markup, ForceReply):
        return

    if m.reply_to_message.text.startswith('#trim_video'):
        c.loop.create_task(Utilities().trim_fn(c, m))
    else:
        c.loop.create_task(Utilities().manual_screenshot_fn(c, m))
