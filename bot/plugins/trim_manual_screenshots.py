from pyrogram import filters
from pyrogram.types import ForceReply

from bot.utils import ProcessTypes
from bot.processes import ProcessFactory
from bot.screenshotbot import ScreenShotBot
from bot.messages import Messages as ms
from bot.config import Config


reply_markup_filter = filters.create(
    lambda _, __, message: message.reply_to_message.reply_markup
    and isinstance(message.reply_to_message.reply_markup, ForceReply)
)


@ScreenShotBot.on_message(filters.private & filters.reply & reply_markup_filter)
async def _(c, m):
    reply_message = await m.reply_text(
        ms.ADDED_TO_QUEUE.format(per_user_process_count=Config.MAX_PROCESSES_PER_USER),
        quote=True,
    )
    if m.reply_to_message.text.startswith("#trim_video"):
        process_type = ProcessTypes.TRIM_VIDEO
    else:
        process_type = ProcessTypes.MANNUAL_SCREENSHOTS

    c.process_pool.new_task(
        (
            m.from_user.id,
            ProcessFactory(
                process_type=process_type,
                client=c,
                input_message=m,
                reply_message=reply_message,
            ),
        )
    )
