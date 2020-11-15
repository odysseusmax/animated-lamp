import time
import datetime

from pyrogram import filters as  Filters

from ..screenshotbot import ScreenShotBot
from ..config import Config


@ScreenShotBot.on_callback_query()
async def __(c, m):
    await foo(c, m, cb=True)


@ScreenShotBot.on_message(Filters.private)
async def _(c, m):
    await foo(c, m)


async def foo(c, m, cb=False):
    chat_id = m.from_user.id
    if int(time.time()) - c.CHAT_FLOOD[chat_id] < Config.SLOW_SPEED_DELAY:
        if cb:
            await m.answer()
        return

    c.CHAT_FLOOD[chat_id] = int(time.time())

    if not await c.db.is_user_exist(chat_id):
        await c.db.add_user(chat_id)
        await c.send_message(
            Config.LOG_CHANNEL,
            f"New User {m.from_user.mention}."
        )

    ban_status = await c.db.get_ban_status(chat_id)
    if ban_status['is_banned']:
        if (datetime.date.today() - datetime.date.fromisoformat(ban_status['banned_on'])).days > ban_status['ban_duration']:
            await c.db.remove_ban(chat_id)
        else:
            return

    last_used_on = await c.db.get_last_used_on(chat_id)
    if last_used_on != datetime.date.today().isoformat():
        await c.db.update_last_used_on(chat_id)

    await m.continue_propagation()
