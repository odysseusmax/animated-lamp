from pyrogram import Client, Filters, ForceReply


@Client.on_message(Filters.private & Filters.reply & Filters.text)
async def _(c, m):
    target = m.reply_to_message
    
    me = await c.get_me()
    if target.from_user.id != me.id:
        return
    
    if not target.reply_markup:
        return
    
    if not isinstance(target.reply_markup, ForceReply):
        return
    await target.delete()
    media_message = await c.get_messages(m.chat.id, m.reply_to_message.message_id)
    print(media_message.reply_to_message)
