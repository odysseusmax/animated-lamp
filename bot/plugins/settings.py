from pyrogram import filters as  Filters

from ..screenshotbot import ScreenShotBot
from ..utils import Utilities


@ScreenShotBot.on_message(Filters.private & Filters.command("settings"))
async def start(c, m):

    await Utilities.display_settings(c, m)
