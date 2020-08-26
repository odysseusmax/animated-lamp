from pyrogram import filters as  Filters

from ..config import Config
from ..screenshotbot import ScreenShotBot


@ScreenShotBot.on_message(Filters.private &  Filters.command("set_watermark"))
async def _(c, m):
    
    if len(m.command) == 1:
        await m.reply_text(
            text="You can add custom watermark text to the screenshots.\n\nUsage: `/set_watermark text`. Text should not Exceed 30 characters.",
            quote=True,
            parse_mode="markdown"
        )
        return
    
    watermark_text = ' '.join(m.command[1:])
    if len(watermark_text) > 30:
        await m.reply_text(
            text=f"The watermark text you provided (__{watermark_text}__) is `{len(watermark_text)}` characters long! You cannot set watermark text greater than 30 characters.",
            quote=True,
            parse_mode="markdown"
        )
        return
    
    await c.db.update_watermark_text(m.chat.id, watermark_text)
    await m.reply_text(
        text=f"You have successfully set __{watermark_text}__ as your watermark text. From now on this will be applied to your screenshots! To remove watermark text see /settings.",
        quote=True,
        parse_mode="markdown"
    )
