import os
import math
import time
import random
import asyncio
import logging
from urllib.parse import urljoin

from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.emoji import *
from bot.config import Config
from bot.messages import Messages

log = logging.getLogger(__name__)


class ProcessTypes:
    SAMPLE_VIDEO = 1
    TRIM_VIDEO = 2
    MANNUAL_SCREENSHOTS = 3
    SCREENSHOTS = 4
    MEDIAINFO = 5


class Utilities:
    @staticmethod
    def TimeFormatter(seconds: int) -> str:
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)
        formatted_txt = f"{days} days, " if days else ""
        formatted_txt += f"{hours} hrs, " if hours else ""
        formatted_txt += f"{minutes} min, " if minutes else ""
        formatted_txt += f"{seconds} sec, " if seconds else ""
        return formatted_txt[:-2]

    @staticmethod
    def is_valid_file(msg):
        if not msg.media:
            return False
        if msg.video:
            return True
        if (msg.document) and any(
            mime in msg.document.mime_type
            for mime in ["video", "application/octet-stream"]
        ):
            return True
        return False

    @staticmethod
    def is_url(text):
        return text.startswith("http")

    @staticmethod
    def get_random_start_at(seconds, dur=0):
        return random.randint(0, seconds - dur)

    @staticmethod
    async def run_subprocess(cmd):
        process = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        return await process.communicate()

    @staticmethod
    async def generate_thumbnail_file(file_path, output_folder):
        os.makedirs(output_folder, exist_ok=True)
        thumb_file = os.path.join(output_folder, "thumb.jpg")
        ffmpeg_cmd = [
            "ffmpeg",
            "-ss",
            "0",
            "-i",
            file_path,
            "-vframes",
            "1",
            "-vf",
            "scale=320:-1",
            "-y",
            str(thumb_file),
        ]
        output = await Utilities.run_subprocess(ffmpeg_cmd)
        log.debug(output)
        if not os.path.exists(thumb_file):
            return None
        return thumb_file

    @staticmethod
    async def generate_stream_link(media_msg):
        media_location = f"/app/bot/DOWNLOADS/{media_msg.from_user.id}{media_msg.message_id}/download.mkv"
        if not os.path.exists(media_location):
            status_msg = await media_msg.reply_text("**Downloading Media File....📥**", quote=True)
            start_time = time.time()
            media_location = await media_msg.download(
                file_name=media_location,
                progress=Utilities.progress_bar,
                progress_args=(start_time, status_msg)
            )
            log.info(media_location)
            await status_msg.delete()
        return media_location

    @staticmethod
    async def progress_bar(current, total, start, msg):
        present = time.time()
        if round((present - start) % 5) == 0 or current == total:
            speed = current / (present - start)
            percentage = current * 100 / total
            time_to_complete = round(((total - current) / speed))
            time_to_complete = Utilities.TimeFormatter(time_to_complete)
            progressbar = "[{0}{1}]".format(
                ''.join([f"{BLACK_MEDIUM_SMALL_SQUARE}" for i in range(math.floor(percentage / 10))]),
                ''.join([f"{WHITE_MEDIUM_SMALL_SQUARE}" for i in range(10 - math.floor(percentage / 10))])
            )
            current_message = f"**Downloading:** {round(percentage, 2)}%\n\n"
            current_message += f"{progressbar}\n\n"
            current_message += f"{HOLLOW_RED_CIRCLE} **Speed**: {Utilities.humanbytes(speed)}/s\n\n"
            current_message += f"{HOLLOW_RED_CIRCLE} **Done**: {Utilities.humanbytes(current)}\n\n"
            current_message += f"{HOLLOW_RED_CIRCLE} **Size**: {Utilities.humanbytes(total)}\n\n"
            current_message += f"{HOLLOW_RED_CIRCLE} **Time Left**: {time_to_complete}\n\n"
            try:
                await msg.edit(
                    text=current_message
                )
            except:
                pass

    @staticmethod
    def humanbytes(size):
        # this code taken from SpEcHiDe Anydl repo
        if not size:
            return 0
        power = 2**10
        n = 0
        Dic_powerN = {0: ' ', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
        while size > power:
            size /= power
            n += 1
        return str(round(size, 2)) + " " + Dic_powerN[n] + 'B'

    @staticmethod
    def TimeFormatter(seconds: int) -> str:
        # this code taken from SpEcHiDe Anydl repo
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)
        formatted_txt = f"{days} days, " if days else ""
        formatted_txt += f"{hours} hrs, " if hours else ""
        formatted_txt += f"{minutes} min, " if minutes else ""
        formatted_txt += f"{seconds} sec, " if seconds else ""
        return formatted_txt[:-2]

    @staticmethod
    async def get_media_info(file_link):
        ffprobe_cmd = [
            "ffprobe",
            "-headers",
            f"IAM:{Config.IAM_HEADER}",
            "-i",
            file_link,
            "-v",
            "quiet",
            "-of",
            "json",
            "-show_streams",
            "-show_format",
            "-show_chapters",
            "-show_programs",
        ]
        data, err = await Utilities.run_subprocess(ffprobe_cmd)
        return data

    @staticmethod
    async def get_dimentions(file_link):
        ffprobe_cmd = [
            "ffprobe",
            "-headers",
            f"IAM:{Config.IAM_HEADER}",
            "-i",
            file_link,
            "-v",
            "error",
            "-show_entries",
            "stream=width,height",
            "-of",
            "csv=p=0:s=x",
            "-select_streams",
            "v:0",
        ]

        output = await Utilities.run_subprocess(ffprobe_cmd)
        log.debug(output)
        try:
            width, height = [int(i.strip()) for i in output[0].decode().split("x")]
        except Exception as e:
            log.debug(e, exc_info=True)
            width, height = 1280, 534
        return width, height

    @staticmethod
    async def get_duration(file_link):
        ffmpeg_dur_cmd = [
            "ffprobe",
            "-headers",
            f"IAM:{Config.IAM_HEADER}",
            "-i",
            file_link,
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "csv=p=0:s=x",
            "-select_streams",
            "v:0",
        ]
        out, err = await Utilities.run_subprocess(ffmpeg_dur_cmd)
        log.debug(f"{out} \n {err}")
        out = out.decode().strip()
        if not out:
            return err.decode()
        duration = round(float(out))
        if duration:
            return duration
        return "No duration!"

    @staticmethod
    async def fix_subtitle_codec(file_link):
        fixable_codecs = ["mov_text"]

        ffmpeg_dur_cmd = [
            "ffprobe",
            "-headers",
            f"IAM:{Config.IAM_HEADER}",
            "-i",
            file_link,
            "-v",
            "error",
            "-select_streams",
            "s",
            "-show_entries",
            "stream=codec_name",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
        ]

        out, err = await Utilities.run_subprocess(ffmpeg_dur_cmd)
        log.debug(f"{out} \n {err}")
        out = out.decode().strip()
        if not out:
            return []

        fix_cmd = []
        codecs = [i.strip() for i in out.split("\n")]
        for indx, codec in enumerate(codecs):
            if any(fixable_codec in codec for fixable_codec in fixable_codecs):
                fix_cmd += [f"-c:s:{indx}", "srt"]

        return fix_cmd

    @staticmethod
    def get_watermark_coordinates(pos, width, height):
        def gcd(m, n):
            return m if not n else gcd(n, m % n)

        def ratio(x, y):
            d = gcd(x, y)
            return x / d, y / d

        a_ratio = ratio(width, height)
        x_fact = 2
        x_pad = round((width * x_fact) / 100)
        y_pad = round((x_pad * a_ratio[1]) / a_ratio[0])

        # https://superuser.com/questions/939357/how-to-position-drawtext-text

        if pos == 0:
            return x_pad, y_pad  # top left
        elif pos == 1:
            return "(w-text_w)/2", f"{y_pad}"  # top center
        elif pos == 2:
            return f"w-tw-{x_pad}", f"{y_pad}"  # top right
        elif pos == 3:
            return x_pad, "(h-text_h)/2"  # center left
        elif pos == 4:
            return "(w-text_w)/2", "(h-text_h)/2"  # centered
        elif pos == 5:
            return f"w-tw-{x_pad}", "(h-text_h)/2"  # center right
        elif pos == 6:
            return x_pad, f"h-th-{y_pad}"  # bottom left
        elif pos == 7:
            return "(w-text_w)/2", f"h-th-{y_pad}"  # bottom center
        else:
            return f"w-tw-{x_pad}", f"h-th-{y_pad}"  # bottom right

    @staticmethod
    async def display_settings(c, m, db, cb=False):
        chat_id = m.from_user.id if cb else m.chat.id

        as_file = await db.is_as_file(chat_id)
        watermark_text = await db.get_watermark_text(chat_id)
        sample_duration = await db.get_sample_duration(chat_id)
        watermark_color_code = await db.get_watermark_color(chat_id)
        watermark_position = await db.get_watermark_position(chat_id)
        screenshot_mode = await db.get_screenshot_mode(chat_id)
        font_size = await db.get_font_size(chat_id)
        mode_txt = "Document" if as_file else "Image"
        wm_txt = watermark_text if watermark_text else "No watermark exists!"
        genmode = "Equally spaced" if screenshot_mode == 0 else "Random screenshots"

        sv_btn = [
            InlineKeyboardButton("⏱ Sample video Duration", "rj"),
            InlineKeyboardButton(f"{sample_duration}s", "set+sv")
        ]
        wc_btn = [
            InlineKeyboardButton("🎨 Watermark Color", "rj"),
            InlineKeyboardButton(f"{Config.COLORS[watermark_color_code]}", "set+wc")
        ]
        fs_btn = [
            InlineKeyboardButton(f"𝔸𝕒 Watermark Font Size", "rj"),
            InlineKeyboardButton(f"{Config.FONT_SIZES_NAME[font_size]}", "set+fs")
        ]
        wp_btn = [
            InlineKeyboardButton("🎭 Watermark Position", "rj"),
            InlineKeyboardButton(f"{Config.POSITIONS[watermark_position]}", "set+wp")
        ]
        as_file_btn = [
            InlineKeyboardButton("📤 Upload Mode", "rj"),
            InlineKeyboardButton(f"{mode_txt}", "set+af")
        ]
        wm_btn = [
            InlineKeyboardButton("💧 Watermark", "rj"),
            InlineKeyboardButton(f"{wm_txt}", "set+wm")
        ]
        sm_btn = [
            InlineKeyboardButton("📸 SS Gen Mode", "rj"),
            InlineKeyboardButton(f"{genmode}", "set+sm")
        ]

        settings_btn = [as_file_btn, wm_btn, wc_btn, fs_btn, wp_btn, sv_btn, sm_btn]

        if cb:
            try:
                await m.message.edit(text=Messages.SETTINGS, reply_markup=InlineKeyboardMarkup(settings_btn))
            except:
                pass
            return

        await m.reply_text(
            text=Messages.SETTINGS,
            quote=True,
            reply_markup=InlineKeyboardMarkup(settings_btn),
        )

    @staticmethod
    def gen_ik_buttons():
        btns = []
        i_keyboard = []
        for i in range(2, 11):
            i_keyboard.append(InlineKeyboardButton(f"{i}", f"scht+{i}"))
            if (i > 2) and (i % 2) == 1:
                btns.append(i_keyboard)
                i_keyboard = []
            if i == 10:
                btns.append(i_keyboard)
        btns.append([InlineKeyboardButton("Manual Screenshots", "mscht")])
        btns.append([InlineKeyboardButton("Trim Video", "trim")])
        btns.append([InlineKeyboardButton("Get Media Information", "mi")])
        return btns
