import time
import datetime

from pyrogram import filters

from bot.screenshotbot import ScreenShotBot
from bot.config import Config
from bot.database import Database


db = Database()


@ScreenShotBot.on_callback_query()
async def __(c, m):
    await foo(c, m, cb=True)


@ScreenShotBot.on_message(filters.private)
async def _(c, m):
    await foo(c, m)


async def foo(c, m, cb=False):
    chat_id = m.from_user.id
    if int(time.time()) - c.CHAT_FLOOD[chat_id] < Config.SLOW_SPEED_DELAY:
        if cb:
            try:
                await m.answer()
            except Exception:
                pass
        return

    c.CHAT_FLOOD[chat_id] = int(time.time())

    if not await db.is_user_exist(chat_id):
        await db.add_user(chat_id)
        await c.send_message(Config.LOG_CHANNEL, f"New User {m.from_user.mention}.")

    ban_status = await db.get_ban_status(chat_id)
    if ban_status["is_banned"]:
        if (
            datetime.date.today() - datetime.date.fromisoformat(ban_status["banned_on"])
        ).days > ban_status["ban_duration"]:
            await db.remove_ban(chat_id)
        else:
            return

    last_used_on = await db.get_last_used_on(chat_id)
    if last_used_on != datetime.date.today().isoformat():
        await db.update_last_used_on(chat_id)

    await m.continue_propagation()
