from pyrogram import filters as Filters

from bot.utils import ProcessTypes
from bot.screenshotbot import ScreenShotBot
from bot.processes import ProcessFactory
from bot.messages import Messages as ms


@ScreenShotBot.on_callback_query(
    Filters.create(lambda _, __, query: query.data.startswith("scht"))
)
async def _(c, m):
    try:
        await m.answer()
    except Exception:
        pass

    await m.edit_message_text(
        ms.ADDED_TO_QUEUE,
    )
    c.process_pool.new_task(
        (
            m.from_user.id,
            ProcessFactory(
                process_type=ProcessTypes.SCREENSHOTS, client=c, input_message=m
            ),
        )
    )
