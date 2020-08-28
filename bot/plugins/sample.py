from pyrogram import filters as  Filters

from ..utils import sample_fn
from ..screenshotbot import ScreenShotBot
from ..config import Config


@ScreenShotBot.on_callback_query(Filters.create(lambda _, __, query: query.data.startswith('smpl')))
async def _(c, m):
    c.loop.create_task(asyncio.wait_for(sample_fn(c, m)), timeout=Config.TIMEOUT)
