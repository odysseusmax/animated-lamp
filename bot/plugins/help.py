from pyrogram import filters as  Filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from ..screenshotbot import ScreenShotBot


HELP_TEXT = """
Hi {}. Welcome to Screenshot Generator Bot. You can use me to generate:

    1. Screenshots.
    2. Sample Video.
    3. Trim Video.

👉 I support any kind of **telegram video file** (streaming video or document video files) provided it --has proper mime-type-- and --is not corrupted--.
👉 I also support **Streaming URLs**. The URL should be a --streaming URL--, --non IP specific--, and --should return proper response codes--.
Just send me the telegram file or the streaming URL.

See /settings to configure bot's behavior.
Use /set_watermark to set custom watermarks to your screenshots.

**General FAQ.**

👉 If the bot dosen't respond to telegram files you forward, first check /start and --confirm bot is alive--. Then make sure the file is a **video file** which satisfies above mentioned conditions.
👉 If bot replies __😟 Sorry! I cannot open the file.__, the file might be --currupted-- or --is malformatted--.

__If issues persists contact my father.__"""


@ScreenShotBot.on_message(Filters.private & Filters.command("help"))
async def help_(c, m):

    await m.reply_text(
        text=HELP_TEXT.format(m.from_user.mention),
        quote=True
    )
