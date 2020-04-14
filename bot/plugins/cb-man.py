from pyrogram import Client, Filters, ForceReply


@Client.on_callback_query(Filters.create(lambda _, query: query.data.startswith('man')))
async def _(c, m):
    await m.edit_message_text(
        "Please provide list of seconds you want to extract separated by space.",
        reply_markup=ForceReply()
    )
