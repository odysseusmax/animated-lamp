from pyrogram import filters as  Filters

from ..screenshotbot import ScreenShotBot
from ..utils import display_settings


@ScreenShotBot.on_message(Filters.private & Filters.command("settings"))
async def start(c, m):
    
    await display_settings(c, m)
