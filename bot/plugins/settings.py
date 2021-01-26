from pyrogram import filters as Filters

from bot.screenshotbot import ScreenShotBot
from bot.utils import Utilities
from bot.database import Database


db = Database()


@ScreenShotBot.on_message(Filters.private & Filters.command("settings"))
async def start(c, m):

    await Utilities.display_settings(c, m, db)
