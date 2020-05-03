import asyncio

from pyrogram import Client, Filters, ForceReply

from bot.utils import sample_fn


@Client.on_callback_query(Filters.create(lambda _, query: query.data.startswith('trim')))
async def _(c, m):
    await m.message.delete(True)
    await c.send_message(
        m.from_user.id,
        'Now send your start and end seconds in the given format and should be upto 10 mins or 600s. \n**start:end**\n\nEg: `400:500` ==> This trims video from 400s to 500s',
        reply_to_message_id=m.message.reply_to_message.message_id,
        reply_markup=ForceReply()
    )
