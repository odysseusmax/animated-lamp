import asyncio

from pyrogram import Client, Filters

from bot.utils import sample_fn


@Client.on_callback_query(Filters.create(lambda _, query: query.data.startswith('smpl')))
async def _(c, m):
    asyncio.create_task(sample_fn(c, m))
