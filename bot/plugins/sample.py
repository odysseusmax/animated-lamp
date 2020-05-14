import asyncio

from pyrogram import Filters

from ..utils import sample_fn
from ..screenshotbot import ScreenShotBot


@ScreenShotBot.on_callback_query(Filters.create(lambda _, query: query.data.startswith('smpl')))
async def _(c, m):
    asyncio.create_task(sample_fn(c, m))
