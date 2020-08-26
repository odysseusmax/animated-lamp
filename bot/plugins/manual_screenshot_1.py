from pyrogram import filters as  Filters
from pyrogram.types import ForceReply

from ..screenshotbot import ScreenShotBot


@ScreenShotBot.on_callback_query(Filters.create(lambda _, __, query: query.data.startswith('mscht')))
async def _(c, m):
    await m.answer()
    dur = m.message.text.markdown.split('\n')[-1]
    await m.message.delete(True)
    await c.send_message(
        m.from_user.id,
        f'#manual_screenshot\n\n{dur}\n\nNow send your list of seconds separated by `,`(comma).\nEg: `0,10,40,60,120`.\nThis will generate screenshots at 0, 10, 40, 60, and 120 seconds. \n\n1. The list can have a maximum of 10 valid positions.\n2. The position has to be greater than or equal to 0, or less than the video length in order to be valid.',
        reply_to_message_id=m.message.reply_to_message.message_id,
        reply_markup=ForceReply()
    )
