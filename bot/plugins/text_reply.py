from pyrogram import Client, Filters, ForceReply


@Client.on_message(Filters.private & Filters.reply & Filters.text)
async def _(c, m):
    target = m.reply_to_message
    media_message = target.reply_to_message
    await target.delete()
    me = await c.get_me()
    if target.from_user.id != me.id:
        return
    
    if not target.reply_markup:
        return
    
    if not isinstance(target.reply_markup, ForceReply):
        return
    
    print(media_message)
