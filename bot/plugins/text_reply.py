from pyrogram import Client, Filters, ForceReply


@Client.on_message(Filters.private & Filters.reply & Filters.text)
async def _(c, m):
    target = m.reply_to_message
    await target.delete()
    me = await c.get_me()
    if target.from_user.id != me.id:
        return
    
    if not target.reply_markup:
        return
    
    if not isinstance(target.reply_markup, ForceReply):
        return
    
    media_message = await c.get_history(
        m.chat.id,
        offset=1,
        limit=1
    )
    print(media_message)
