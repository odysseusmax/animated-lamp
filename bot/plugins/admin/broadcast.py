import traceback
import datetime
import asyncio
import string
import random
import time
import io

from pyrogram import filters as Filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait, InputUserDeactivated, UserIsBlocked, PeerIdInvalid

from bot.config import Config
from bot.screenshotbot import ScreenShotBot


async def send_msg(user_id, message):
    try:
        await message.forward(chat_id=user_id, as_copy=True)
        return 200, None
    except FloodWait as e:
        await asyncio.sleep(e.x)
        return send_msg(user_id, message)
    except InputUserDeactivated:
        return 400, f"{user_id} : deactivated\n"
    except UserIsBlocked:
        return 400, f"{user_id} : blocked the bot\n"
    except PeerIdInvalid:
        return 400, f"{user_id} : user id invalid\n"
    except Exception as e:
        return 500, f"{user_id} : {traceback.format_exc()}\n"



@ScreenShotBot.on_message(Filters.private & Filters.command("broadcast") & Filters.user(Config.AUTH_USERS) & Filters.reply)
async def broadcast_(c, m):
    all_users = await c.db.get_all_users()

    broadcast_msg = m.reply_to_message

    while True:
        broadcast_id = ''.join([random.choice(string.ascii_letters) for i in range(3)])
        if not c.broadcast_ids.get(broadcast_id):
            break

    out = await m.reply_text(
        text = f"Broadcast initiated! You will be notified with log file when all the users are notified.",
        reply_markup = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("Cancel Broadcast", callback_data=f"cncl_bdct+{broadcast_id}"),
                    InlineKeyboardButton("View broadcast status", callback_data=f"sts_bdct+{broadcast_id}")
                ]
            ]
        )
    )
    start_time = time.time()
    total_users = await c.db.total_users_count()
    done = 0
    failed = 0
    success = 0

    c.broadcast_ids[broadcast_id] = dict(
        total = total_users,
        current = done,
        failed = failed,
        success = success
    )
    log_file = io.BytesIO()
    log_file.name = f'broadcast_{broadcast_id}.txt'
    broadcast_log = ''
    async for user in all_users:
        await asyncio.sleep(1)
        sts, msg = await send_msg(
            user_id = int(user['id']),
            message = broadcast_msg
        )
        if msg is not None:
            broadcast_log += msg

        if sts == 200:
            success += 1
        else:
            failed += 1

        if sts == 400:
            await c.db.delete_user(user['id'])

        done += 1
        if c.broadcast_ids.get(broadcast_id) is None:
            break
        else:
            c.broadcast_ids[broadcast_id].update(
                dict(
                    current = done,
                    failed = failed,
                    success = success
                )
            )
    log_file.write(broadcast_log.encode())
    if c.broadcast_ids.get(broadcast_id):
        c.broadcast_ids.pop(broadcast_id)
    completed_in = datetime.timedelta(seconds=int(time.time()-start_time))

    await asyncio.sleep(3)

    await out.delete()

    if failed == 0:
        await m.reply_text(
            text=f"broadcast completed in `{completed_in}`\n\nTotal users {total_users}.\nTotal done {done}, {success} success and {failed} failed.",
            quote=True
        )
    else:
        await m.reply_document(
            document=log_file,
            caption=f"broadcast completed in `{completed_in}`\n\nTotal users {total_users}.\nTotal done {done}, {success} success and {failed} failed.",
            quote=True
        )
