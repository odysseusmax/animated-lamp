import asyncio

from pyrogram import Client, Filters

from bot.utils import screenshot_fn


@Client.on_callback_query(Filters.create(lambda _, query: query.data.startswith('scht')))
async def _(c, m):
    asyncio.create_task(screenshot_fn(c, m))
