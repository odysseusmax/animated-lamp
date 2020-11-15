import os
import random
import asyncio
import logging
from urllib.parse import urljoin

from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from ..config import Config


log = logging.getLogger(__name__)


class ProcessCounter:
    def __init__(self, store, item):
        self.store = store
        self.item = item

    def __enter__(self):
        self.store[self.item] += 1

    def __exit__(self, exc_type, exc_value, traceback):
        self.store[self.item] -= 1

    async def __aexit__(self, exc_type, exc_value, traceback):
        self.__exit__(exc_type, exc_value, traceback)

    async def __aenter__(self):
        self.__enter__()


class CommonUtils:

    @staticmethod
    def is_valid_file(msg):
        if not msg.media:
            return False
        if msg.video:
            return True
        if (msg.document) and any(mime in msg.document.mime_type for mime in ['video', "application/octet-stream"]):
            return True
        return False

    @staticmethod
    def is_url(text):
        return text.startswith('http')

    @staticmethod
    def get_random_start_at(seconds, dur=0):
        return random.randint(0, seconds-dur)

    @staticmethod
    async def run_subprocess(cmd):
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        return await process.communicate()

    @staticmethod
    async def generate_thumbnail_file(file_path, uid):
        output_folder = Config.THUMB_OP_FLDR.joinpath(uid)
        os.makedirs(output_folder, exist_ok=True)

        thumb_file = output_folder.joinpath('thumb.jpg')
        ffmpeg_cmd = ['ffmpeg', '-ss', '0', '-i', file_path, '-vframes', '1', '-vf', 'scale=320:-1', '-y', str(thumb_file)]
        output = await CommonUtils.run_subprocess(ffmpeg_cmd)
        log.debug(output)
        if not thumb_file.exists():
            return None
        return thumb_file

    @staticmethod
    def generate_stream_link(media_msg):
        file_id = media_msg.message_id
        chat_id = media_msg.chat.id
        return urljoin(Config.HOST, f"file/{chat_id}/{file_id}")

    @staticmethod
    async def get_media_info(file_link):
        ffprobe_cmd = ['ffprobe', '-headers', f'IAM:{Config.IAM_HEADER}', '-i', file_link, '-v', 'quiet', '-of', 'json', '-show_streams',
                       '-show_format', '-show_chapters', '-show_programs']
        data, err = await CommonUtils.run_subprocess(ffprobe_cmd)
        return data

    @staticmethod
    async def get_dimentions(file_link):
        ffprobe_cmd = ['ffprobe', '-headers', f'IAM:{Config.IAM_HEADER}', '-i', file_link, '-v', 'error', '-show_entries',
                       'stream=width,height', '-of', 'csv=p=0:s=x', '-select_streams', 'v:0']

        output = await CommonUtils.run_subprocess(ffprobe_cmd)
        log.debug(output)
        try:
            width, height = [int(i.strip()) for i in output[0].decode().split('x')]
        except Exception as e:
            log.debug(e, exc_info=True)
            width, height = 1280, 534
        return width, height

    @staticmethod
    async def get_duration(file_link):
        ffmpeg_dur_cmd = ['ffprobe', '-headers', f'IAM:{Config.IAM_HEADER}', '-i', file_link, '-v', 'error', '-show_entries',
                          'format=duration', '-of', 'csv=p=0:s=x', '-select_streams', 'v:0', ]
        out, err = await CommonUtils.run_subprocess(ffmpeg_dur_cmd)
        log.debug(f"{out} \n {err}")
        out = out.decode().strip()
        if not out:
            return err.decode()
        duration = round(float(out))
        if duration:
            return duration
        return 'No duration!'

    @staticmethod
    async def fix_subtitle_codec(file_link):
        fixable_codecs = ['mov_text']

        ffmpeg_dur_cmd = ['ffprobe', '-headers', f'IAM:{Config.IAM_HEADER}', '-i', file_link, '-v', 'error', '-select_streams', 's',
                          '-show_entries', 'stream=codec_name', '-of', 'default=noprint_wrappers=1:nokey=1']

        out, err = await CommonUtils.run_subprocess(ffmpeg_dur_cmd)
        log.debug(f"{out} \n {err}")
        out = out.decode().strip()
        if not out:
            return []

        fix_cmd = []
        codecs = [i.strip() for i in out.split('\n')]
        for indx, codec in enumerate(codecs):
            if any(fixable_codec in codec for fixable_codec in fixable_codecs):
                fix_cmd += [f'-c:s:{indx}', 'srt']

        return fix_cmd

    @staticmethod
    def get_watermark_coordinates(pos, width, height):

        def ratio(x, y):
            gcd = lambda m,n: m if not n else gcd(n,m%n)
            d = gcd(x, y)
            return x/d, y/d

        a_ratio = ratio(width, height)
        x_fact = 2
        x_pad = round((width*x_fact) / 100)
        y_pad = round((x_pad * a_ratio[1])/a_ratio[0])

        # https://superuser.com/questions/939357/how-to-position-drawtext-text

        if pos == 0:
            return x_pad, y_pad # top left
        elif pos == 1:
            return '(w-text_w)/2', f'{y_pad}' # top center
        elif pos == 2:
            return f'w-tw-{x_pad}', f'{y_pad}' # top right
        elif pos == 3:
            return x_pad, '(h-text_h)/2' # center left
        elif pos == 4:
            return '(w-text_w)/2', '(h-text_h)/2' # centered
        elif pos == 5:
            return f'w-tw-{x_pad}', '(h-text_h)/2' # center right
        elif pos == 6:
            return x_pad, f'h-th-{y_pad}' # bottom left
        elif pos == 7:
            return '(w-text_w)/2', f'h-th-{y_pad}' # bottom center
        else:
            return f'w-tw-{x_pad}', f'h-th-{y_pad}' # bottom right


    @staticmethod
    async def display_settings(c, m, cb=False):
        chat_id = m.from_user.id if cb else m.chat.id

        as_file = await c.db.is_as_file(chat_id)
        as_round = await c.db.is_as_round(chat_id)
        watermark_text = await c.db.get_watermark_text(chat_id)
        sample_duration = await c.db.get_sample_duration(chat_id)
        watermark_color_code = await c.db.get_watermark_color(chat_id)
        watermark_position = await c.db.get_watermark_position(chat_id)
        screenshot_mode = await c.db.get_screenshot_mode(chat_id)
        font_size = await c.db.get_font_size(chat_id)

        sv_btn = [
            InlineKeyboardButton("Sample Video Duration", 'rj'),
            InlineKeyboardButton(f"{sample_duration}s", 'set+sv')
        ]
        wc_btn = [
            InlineKeyboardButton("Watermark Color", 'rj'),
            InlineKeyboardButton(f"{Config.COLORS[watermark_color_code]}", 'set+wc')
        ]
        fs_btn = [
            InlineKeyboardButton("Watermark Font Size", 'rj'),
            InlineKeyboardButton(f"{Config.FONT_SIZES_NAME[font_size]}", 'set+fs')
        ]
        wp_btn = [
            InlineKeyboardButton("Watermark Position", 'rj'),
            InlineKeyboardButton(f"{Config.POSITIONS[watermark_position]}", 'set+wp')
        ]
        as_file_btn = [InlineKeyboardButton("Upload Mode", 'rj')]
        wm_btn = [InlineKeyboardButton("Watermark", 'rj')]
        sm_btn = [InlineKeyboardButton("Screenshot Generation Mode", 'rj')]


        if as_file:
            as_file_btn.append(InlineKeyboardButton("📁 Uploading as Document.", 'set+af'))
        else:
            as_file_btn.append(InlineKeyboardButton("🖼️ Uploading as Image.", 'set+af'))

        if watermark_text:
            wm_btn.append(InlineKeyboardButton(f"{watermark_text}", 'set+wm'))
        else:
            wm_btn.append(InlineKeyboardButton("No watermark exists!", 'set+wm'))

        if screenshot_mode == 0:
            sm_btn.append(InlineKeyboardButton("Equally spaced screenshots", 'set+sm'))
        else:
            sm_btn.append(InlineKeyboardButton("Random screenshots", 'set+sm'))

        settings_btn = [as_file_btn, wm_btn, wc_btn, fs_btn, wp_btn, sv_btn, sm_btn]

        if cb:
            try:
                await m.edit_message_reply_markup(
                    InlineKeyboardMarkup(settings_btn)
                )
            except:
                pass
            return

        await m.reply_text(
            text = f"Here You can configure my behavior.\n\nPress the button to change the settings.",
            quote=True,
            reply_markup=InlineKeyboardMarkup(settings_btn)
        )

    @staticmethod
    def gen_ik_buttons():
        btns = []
        i_keyboard = []
        for i in range(2, 11):
            i_keyboard.append(
                InlineKeyboardButton(f"{i}", f"scht+{i}"))
            if (i>2) and (i%2) == 1:
                btns.append(i_keyboard)
                i_keyboard = []
            if i==10:
                btns.append(i_keyboard)
        btns.append([InlineKeyboardButton('Manual Screenshots!', 'mscht')])
        btns.append([InlineKeyboardButton('Trim Video!', 'trim')])
        btns.append([InlineKeyboardButton('Get Media Information', 'mi')])
        return btns
