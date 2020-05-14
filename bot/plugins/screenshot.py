import asyncio

from pyrogram import Filters

from ..utils import screenshot_fn
from ..screenshotbot import ScreenShotBot


@ScreenShotBot.on_callback_query(Filters.create(lambda _, query: query.data.startswith('scht')))
async def _(c, m):
    asyncio.create_task(screenshot_fn(c, m))
