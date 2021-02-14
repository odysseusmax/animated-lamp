from pyrogram import filters

from bot.screenshotbot import ScreenShotBot
from bot.utils import Utilities
from bot.config import Config
from bot.database import Database


db = Database()


@ScreenShotBot.on_callback_query(
    filters.create(lambda _, __, query: query.data.startswith("set"))
)
async def settings_cb(c, m):
    try:
        _, typ, action = m.data.split("+")  # Reverse compatibility.
    except Exception:
        _, typ = m.data.split("+")
    chat_id = m.from_user.id
    alert_text = "Not supported action."

    if typ == "af":
        as_file = await db.is_as_file(chat_id)
        await db.update_as_file(chat_id, not as_file)
        alert_text = "Successfully changed screenshot upload mode!"

    elif typ == "wm":
        watermark_text = await db.get_watermark_text(chat_id)
        if watermark_text:
            await db.update_watermark_text(chat_id)
            alert_text = "Successfully removed watermark text."
        else:
            alert_text = "Use /set_watermark to add new watermark text."

    elif typ == "sv":
        sample_duration = await db.get_sample_duration(chat_id)
        if sample_duration + 30 >= 180:
            sample_duration = 0
        sample_duration += 30
        await db.update_sample_duration(chat_id, sample_duration)
        alert_text = f"Sample video duration changed to {sample_duration}s"

    elif typ == "wc":
        watermark_color_code = await db.get_watermark_color(chat_id)
        if watermark_color_code + 1 == len(Config.COLORS):
            watermark_color_code = -1
        watermark_color_code += 1
        await db.update_watermark_color(chat_id, watermark_color_code)
        alert_text = f"Successfully changed watermark text color to {Config.COLORS[watermark_color_code]}"

    elif typ == "sm":
        screenshot_mode = await db.get_screenshot_mode(chat_id)
        if screenshot_mode == 0:
            screenshot_mode = 1
        else:
            screenshot_mode = 0
        await db.update_screenshot_mode(chat_id, screenshot_mode)
        alert_text = "Successfully changed screenshot generation mode"

    elif typ == "fs":
        font_size = await db.get_font_size(chat_id)
        if font_size == len(Config.FONT_SIZES) - 1:
            font_size = -1
        font_size += 1
        await db.update_font_size(chat_id, font_size)
        alert_text = (
            f"Successfully changed font size to {Config.FONT_SIZES_NAME[font_size]}"
        )
    elif typ == "wp":
        current_pos = await db.get_watermark_position(chat_id)
        if current_pos == len(Config.POSITIONS) - 1:
            current_pos = -1
        current_pos += 1
        await db.update_watermark_position(chat_id, current_pos)
        alert_text = f"Successfully changed watermark position to {Config.POSITIONS[current_pos]}"

    await m.answer(alert_text, show_alert=True)

    await Utilities.display_settings(c, m, db, cb=True)


@ScreenShotBot.on_callback_query(
    filters.create(lambda _, __, query: query.data.startswith("rj"))
)
async def _(c, m):
    await m.answer("😂 press the other button 😂")
