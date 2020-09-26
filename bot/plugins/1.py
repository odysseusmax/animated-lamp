import time

from pyrogram import filters as  Filters

from ..screenshotbot import ScreenShotBot
from ..config import Config


@ScreenShotBot.on_callback_query()
async def __(c, m):
    chat_id = m.from_user.id
    await foo(c, m, chat_id, cb=True)


@ScreenShotBot.on_message(Filters.private)
async def _(c, m):
    chat_id = m.chat.id
    await foo(c, m, chat_id)


async def foo(c, m, chat_id, cb=False):
    if not c.CHAT_FLOOD.get(chat_id):
        c.CHAT_FLOOD[chat_id] = int(time.time()) - Config.SLOW_SPEED_DELAY-1

    if int(time.time()) - c.CHAT_FLOOD.get(chat_id) < Config.SLOW_SPEED_DELAY:
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

    await m.continue_propagation()
