import os
import re
import uuid
import time
import shlex
import random
import asyncio
import datetime
import traceback

from pyrogram import InputMediaPhoto, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait

from config import Config
from bot import user, db, CURRENT_PROCESSES



def is_valid_file(msg):
    if not msg.media:
        return False
    if msg.video:
        return True
    if (msg.document) and any(mime in msg.document.mime_type for mime in ['video', "application/octet-stream"]):
        return True
    return False

def is_url(text):
    return text.startswith('http')


def get_random_start_at(seconds, dur=0):
    return random.randint(0, seconds-dur)


async def run_subprocess(cmd):
    process = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    return await process.communicate()


async def generate_thumbnail_file(file_path, uid):
    output_folder = Config.THUMB_OP_FLDR.joinpath(uid)
    if not output_folder.exists():
        os.makedirs(output_folder)
    
    thumb_file = output_folder.joinpath('thumb.jpg')
    ffmpeg_cmd = f"ffmpeg -ss 0 -i '{file_path}' -vframes 1 '{thumb_file}'"
    output = await run_subprocess(ffmpeg_cmd)
    if not thumb_file.exists():
        return None
    return thumb_file


async def generate_stream_link(media_msg):
    middle_msg = await media_msg.forward(Config.MIDDLE_MAN)
    middle_msg = await user.get_messages(Config.MIDDLE_MAN, middle_msg.message_id)
    link_req_msg = await middle_msg.forward(Config.LINK_GEN_BOT)
    await user.read_history(Config.LINK_GEN_BOT)
    await asyncio.sleep(2)
    link_msg = None
    async for mes in user.iter_history(Config.LINK_GEN_BOT, limit=10):
        if mes.reply_to_message and mes.reply_to_message.message_id == link_req_msg.message_id:
            link_msg = mes
    if link_msg is None:
        return None
    return link_msg.text


async def get_duration(input_file_link):
    ffmpeg_dur_cmd = f"ffprobe -hide_banner -i {shlex.quote(input_file_link)}"
    #print(ffmpeg_dur_cmd)
    output = await run_subprocess(ffmpeg_dur_cmd)
    #print(output[1].decode())
    duration = re.findall("Duration: (.*?)\.", output[1].decode())
    if not duration:
        return output[1].decode()
    
    hh, mm, ss = [int(i) for i in duration[0].split(":")]
    seconds = hh*60*60 + mm*60 + ss
    return seconds


async def edit_message_text(m, **kwargs):
    while True:
        try:
            return await m.edit_message_text(**kwargs)
        except FloodWait as e:
            await asyncio.sleep(e.x)
        except:
            break


async def display_settings(m, cb=False):
    chat_id = m.from_user.id if cb else m.chat.id
    
    as_file = await db.is_as_file(chat_id)
    watermark_text = await db.get_watermark_text(chat_id)
    sample_duration = await db.get_sample_duration(chat_id)
    watermark_color_code = await db.get_watermark_color(chat_id)
    
    
    if as_file:
        as_file_btn = [InlineKeyboardButton("Upload Mode", 'rj'), InlineKeyboardButton("📁 Uploading as Document.", 'set+af+0')]
    else:
        as_file_btn = [InlineKeyboardButton("Upload Mode", 'rj'), InlineKeyboardButton("🖼️ Uploading as Image.", 'set+af+1')]
    
    if watermark_text:
        wm_btn = [InlineKeyboardButton("Watermark", 'rj'), InlineKeyboardButton(f"{watermark_text}", 'set+wm+0')]
    else:
        wm_btn = [InlineKeyboardButton("Watermark", 'rj'), InlineKeyboardButton("No watermark exists!", 'set+wm+1')]
    
    sv_btn = [InlineKeyboardButton("Sample Video Duration", 'rj'), InlineKeyboardButton(f"{sample_duration}s", 'set+sv+1')]
    wc_btn = [InlineKeyboardButton("Watermark Color", 'rj'), InlineKeyboardButton(f"{Config.COLORS[watermark_color_code]}", 'set+wc+1')]
    
    settings_btn = [as_file_btn, wm_btn, wc_btn, sv_btn]
    
    if cb:
        await m.edit_message_reply_markup(
            InlineKeyboardMarkup(settings_btn)
        )
        return
    
    await m.reply_text(
        text = f"Here You can configure the bot's behavior.",
        quote=True,
        reply_markup=InlineKeyboardMarkup(settings_btn)
    )


async def screenshot_fn(c, m):
    
    chat_id = m.from_user.id
    if CURRENT_PROCESSES.get(chat_id, 0) == Config.MAX_PROCESSES_PER_USER:
        await m.answer('You have reached the maximum parallel processes! Try again after one of them finishes.', alert=True)
        return
    if not CURRENT_PROCESSES.get(chat_id):
        CURRENT_PROCESSES[chat_id] = 0
    CURRENT_PROCESSES[chat_id] += 1
    
    _, num_screenshots = m.data.split('+')
    num_screenshots = int(num_screenshots)
    media_msg = m.message.reply_to_message
    #print(media_msg)
    if media_msg.empty:
        await edit_message_text(m, text='Why did you delete the file 😠, Now i cannot help you 😒.')
        CURRENT_PROCESSES[chat_id] -= 1
        return
    
    uid = str(uuid.uuid4())
    output_folder = Config.SCRST_OP_FLDR.joinpath(uid)
    if not output_folder.exists():
        os.makedirs(output_folder)
    
    if media_msg.media:
        typ = 1
    else:
        typ = 2
    
    try:
        start_time = time.time()
        
        await edit_message_text(m, text='Processing your request, Please wait! 😴')
        
        if typ == 2:
            file_link = media_msg.text
        else:
            file_link = await generate_stream_link(media_msg)
            if file_link is None:
                await edit_message_text(m, text="😟 Sorry! I cannot help you right now, I'm having hard time processing the file.")
                l = await media_msg.forward(Config.LOG_CHANNEL)
                await l.reply_text(f'@{Config.LINK_GEN_BOT} did not respond with stream url', True)
                CURRENT_PROCESSES[chat_id] -= 1
                return
            
        await edit_message_text(m, text='😀 Generating screenshots!')
        
        duration = await get_duration(file_link)
        if isinstance(duration, str):
            await edit_message_text(m, text="😟 Sorry! I cannot open the file.")
            l = await media_msg.forward(Config.LOG_CHANNEL)
            await l.reply_text(f'stream link : {file_link}\n\nRequested screenshots: {num_screenshots} \n\n{duration}', True)
            CURRENT_PROCESSES[chat_id] -= 1
            return

        reduced_sec = duration - int(duration*2 / 100)
        print(f"Total seconds: {duration}, Reduced seconds: {reduced_sec}")
        as_file = await db.is_as_file(m.from_user.id)
        
        screenshots = []
        watermark = await db.get_watermark_text(m.from_user.id)
        watermark_color_code = await db.get_watermark_color(m.from_user.id)
        watermark_color = Config.COLORS[watermark_color_code]
        ffmpeg_errors = ''
        
        for i in range(1, 1+num_screenshots):
            sec = get_random_start_at(reduced_sec)
            thumbnail_template = output_folder.joinpath(f'{i}.png')
            print(sec)
            ffmpeg_cmd = f"ffmpeg -hide_banner -ss {sec} -i {shlex.quote(file_link)} -vf \"drawtext=fontcolor={watermark_color}:fontsize=40:x=(W-tw)/2:y=H-th-10:text='{shlex.quote(watermark)}'\" -vframes 1 '{thumbnail_template}'"
            output = await run_subprocess(ffmpeg_cmd)
            await edit_message_text(m, text=f'`{i}` of `{num_screenshots}` generated!')
            if thumbnail_template.exists():
                if as_file:
                    screenshots.append({
                        'document':str(thumbnail_template),
                        'caption':f"ScreenShot at {datetime.timedelta(seconds=sec)}"
                    })
                else:
                    screenshots.append(
                        InputMediaPhoto(
                            str(thumbnail_template),
                            caption=f"ScreenShot at {datetime.timedelta(seconds=sec)}"
                        )
                    )
                continue
            ffmpeg_errors += output[1].decode() + '\n\n'
        
        #print(screenshots)
        if not screenshots:
            await edit_message_text(m, text='😟 Sorry! Screenshot generation failed possibly due to some infrastructure failure 😥.')
            
            l = await media_msg.forward(Config.LOG_CHANNEL)
            if ffmpeg_errors:
                error_file = f"{uid}-errors.txt"
                with open(error_file, 'w') as f:
                    f.write(ffmpeg_errors)
                await l.reply_document(error_file, caption=f"stream link : {file_link}\n\n{num_screenshots} screenshots where requested and Screen shots where not generated.")
                os.remove(error_file)
            else:
                await l.reply_text(f'stream link : {file_link}\n\n{num_screenshots} screenshots where requested and Screen shots where not generated.', True)
            CURRENT_PROCESSES[chat_id] -= 1
            return
        
        await edit_message_text(m, text=f'🤓 You requested {num_screenshots} screenshots and {len(screenshots)} screenshots generated, Now starting to upload!')
        
        await media_msg.reply_chat_action("upload_photo")
        
        if as_file:
            aws = [media_msg.reply_document(quote=True, **photo) for photo in screenshots]
            await asyncio.gather(*aws)
        else:
            await media_msg.reply_media_group(screenshots, True)
        
        await edit_message_text(m, text=f'Successfully completed process in {datetime.timedelta(seconds=int(time.time()-start_time))}\n\nIf You find me helpful, please rate me [here](tg://resolve?domain=botsarchive&post=1206)')
        CURRENT_PROCESSES[chat_id] -= 1
        
    except:
        traceback.print_exc()
        await edit_message_text(m, text='😟 Sorry! Screenshot generation failed possibly due to some infrastructure failure 😥.')
        
        l = await media_msg.forward(Config.LOG_CHANNEL)
        await l.reply_text(f'{num_screenshots} screenshots where requested and some error occoured\n\n{traceback.format_exc()}', True)
        CURRENT_PROCESSES[chat_id] -= 1


async def sample_fn(c, m):
    chat_id = m.from_user.id
    if CURRENT_PROCESSES.get(chat_id, 0) == Config.MAX_PROCESSES_PER_USER:
        await m.answer('You have reached the maximum parallel processes! Try again after one of them finishes.', alert=True)
        return
    if not CURRENT_PROCESSES.get(chat_id):
        CURRENT_PROCESSES[chat_id] = 0
    CURRENT_PROCESSES[chat_id] += 1
    
    media_msg = m.message.reply_to_message
    if media_msg.empty:
        await edit_message_text(m, text='Why did you delete the file 😠, Now i cannot help you 😒.')
        CURRENT_PROCESSES[chat_id] -= 1
        return
    
    uid = str(uuid.uuid4())
    output_folder = Config.SMPL_OP_FLDR.joinpath(uid)
    if not output_folder.exists():
        os.makedirs(output_folder)
    
    if media_msg.media:
        typ = 1
    else:
        typ = 2
    
    try:
        start_time = time.time()
        
        await edit_message_text(m, text='Processing your request, Please wait! 😴')
        
        if typ == 2:
            file_link = media_msg.text
        else:
            file_link = await generate_stream_link(media_msg)
            if file_link is None:
                await edit_message_text(m, text="😟 Sorry! I cannot help you right now, I'm having hard time processing the file.")
                l = await media_msg.forward(Config.LOG_CHANNEL)
                await l.reply_text(f'@{Config.LINK_GEN_BOT} did not respond with stream url', True)
                CURRENT_PROCESSES[chat_id] -= 1
                return
            
        await edit_message_text(m, text='😀 Generating Sample Video! This might take some time.')
        
        duration = await get_duration(file_link)
        if isinstance(duration, str):
            await edit_message_text(m, text="😟 Sorry! I cannot open the file.")
            l = await media_msg.forward(Config.LOG_CHANNEL)
            await l.reply_text(f'stream link : {file_link}\n\nSample video requested\n\n{duration}', True)
            CURRENT_PROCESSES[chat_id] -= 1
            return
        
        reduced_sec = duration - int(duration*10 / 100)
        print(f"Total seconds: {duration}, Reduced seconds: {reduced_sec}")
        sample_duration = await db.get_sample_duration(m.from_user.id)
        
        start_at = get_random_start_at(reduced_sec, sample_duration)
        
        sample_file = output_folder.joinpath(f'sample_video.mkv')
        
        ffmpeg_cmd = f"ffmpeg -hide_banner -ss {start_at} -i {shlex.quote(file_link)} -t {sample_duration} -map 0 -c copy {sample_file}"
        output = await run_subprocess(ffmpeg_cmd)
        #print(output[1].decode())
        
        if not sample_file.exists():
            await edit_message_text(m, text='😟 Sorry! Sample video generation failed possibly due to some infrastructure failure 😥.')
            
            l = await media_msg.forward(Config.LOG_CHANNEL)
            await l.reply_text(f'stream link : {file_link}\n\n duration {sample_duration} sample video generation failed\n\n{output[1].decode()}', True)
            CURRENT_PROCESSES[chat_id] -= 1
            return
        
        thumb = await generate_thumbnail_file(sample_file, uid)
        
        await edit_message_text(m, text=f'🤓 Sample video was generated successfully!, Now starting to upload!')
        
        await media_msg.reply_chat_action("upload_video")
        
        await media_msg.reply_video(
            video=sample_file, 
            quote=True,
            caption=f"Sample video. {sample_duration}s from {datetime.timedelta(seconds=start_at)}",
            duration=sample_duration,
            thumb=thumb,
            supports_streaming=True
        )
        
        await edit_message_text(m, text=f'Successfully completed process in {datetime.timedelta(seconds=int(time.time()-start_time))}\n\nIf You find me helpful, please rate me [here](tg://resolve?domain=botsarchive&post=1206)')
        CURRENT_PROCESSES[chat_id] -= 1
        
    except:
        traceback.print_exc()
        await edit_message_text(m, text='😟 Sorry! Sample video generation failed possibly due to some infrastructure failure 😥.')
        
        l = await media_msg.forward(Config.LOG_CHANNEL)
        await l.reply_text(f'sample video requested and some error occoured\n\n{traceback.format_exc()}', True)
        CURRENT_PROCESSES[chat_id] -= 1


def gen_ik_buttons():
    btns = []
    i_keyboard = []
    for i in range(2, 11):
        i_keyboard.append(
            InlineKeyboardButton(
                f"{i}",
                f"scht+{i}"
            )
        )
        if (i>2) and (i%2) == 1:
            btns.append(i_keyboard)
            i_keyboard = []
        if i==10:
            btns.append(i_keyboard)
    return btns
