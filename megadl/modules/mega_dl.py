import os
import shutil
import filetype
import moviepy.editor
import time
import subprocess
import json

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from hurry.filesize import size
from functools import partial
from asyncio import get_running_loop
from genericpath import isfile
from posixpath import join

from megadl.helpers_nexa.account import m
from megadl.helpers_nexa.mega_help import progress_for_pyrogram, humanbytes, send_errors, send_logs
from config import Config

# path we gonna give the download
basedir = Config.DOWNLOAD_LOCATION
# Telegram's max file size
TG_MAX_FILE_SIZE = Config.TG_MAX_SIZE

# Automatic Url Detect (From stackoverflow. Can't find link lol)
MEGA_REGEX = (r"^((?:https?:)?\/\/)"
              r"?((?:www)\.)"
              r"?((?:mega\.nz))"
              r"(\/)([-a-zA-Z0-9()@:%_\+.~#?&//=]*)([\w\-]+)(\S+)?$")

# Download Mega Link
def DownloadMegaLink(url, alreadylol, download_msg):
    try:
        m.download_url(url, alreadylol, statusdl_msg=download_msg)
    except Exception as e:
        send_errors(e=e)


@Client.on_message(filters.regex(MEGA_REGEX) & filters.private)
async def megadl(megabot: Client, message: Message):
    url = message.text
    userpath = str(message.from_user.id)
    the_chat_id = str(message.chat.id)
    alreadylol = basedir + "/" + userpath
    # Getting file size before download
    try:
        json_f_info = m.get_public_url_info(url)
        dumped_j_info = json.dumps(json_f_info)
        loaded_f_info = json.loads(dumped_j_info)
        mega_f_size = loaded_f_info['size']
        readable_f_size = size(mega_f_size)
        if mega_f_size > TG_MAX_FILE_SIZE:
            await message.reply_text(f"**Detected File Size:** `{readable_f_size}` \n**Accepted File Size:** `2GB` \n\nOops! File Size is too large to send in Telegram")
            return
    except Exception as e:
        await message.reply_text(f"**Error:** `{e}`")
        await send_errors(e=e)
        return
    # Temp fix for the https://github.com/Itz-fork/Mega.nz-Bot/issues/11
    if os.path.isdir(alreadylol):
        await message.reply_text("`Already One Process is Going On. Please wait until it's finished!`")
        return
    else:
        os.makedirs(alreadylol)
    try:
        download_msg = await message.reply_text("**Starting to Download The Content! This may take while 😴**", reply_markup=CANCEL_BUTTN)
        await send_logs(user_id=userpath, mchat_id=the_chat_id, mega_url=url, download_logs=True)
        loop = get_running_loop()
        await loop.run_in_executor(None, partial(DownloadMegaLink, url, alreadylol, download_msg))
        getfiles = [f for f in os.listdir(alreadylol) if isfile(join(alreadylol, f))]
        files = getfiles[0]
        magapylol = f"{alreadylol}/{files}"
        await download_msg.edit("**Successfully Downloaded The Content!**")
    except Exception as e:
        if os.path.isdir(alreadylol):
            await download_msg.edit(f"**Error:** `{e}`")
            shutil.rmtree(basedir + "/" + userpath)
            await send_errors(e=e)
        return
    # If user cancelled the process bot will return into telegram again lmao
    if os.path.isdir(alreadylol) is False:
        return
    else:
        pass
    lmaocheckdis = os.stat(alreadylol).st_size
    readablefilesize = size(lmaocheckdis) # Convert Bytes into readable size
    # below code for checking file size isn't needed at all. but i'm not sure about my codes so...
    if lmaocheckdis > TG_MAX_FILE_SIZE:
        await download_msg.edit(f"**Detected File Size:** `{readablefilesize}` \n**Accepted File Size:** `2GB` \n\nOops! File Size is too large to send in Telegram")
        shutil.rmtree(basedir + "/" + userpath)
        return
    else:
        start_time = time.time()
        guessedfilemime = filetype.guess(f"{magapylol}") # Detecting file type
        if not guessedfilemime.mime:
            await download_msg.edit("**Trying to Upload Now!** \n\n**Error:** `Can't Get File Mime Type! Sending as a Document!`")
            await message.reply_document(magapylol, progress=progress_for_pyrogram, progress_args=("**Trying to Upload Now!** \n", download_msg, start_time))
            await download_msg.edit(f"**Successfully Uploaded**")
            shutil.rmtree(basedir + "/" + userpath)
            return
        filemimespotted = guessedfilemime.mime
        # Checking If it's a gif
        if "image/gif" in filemimespotted:
            await download_msg.edit("**Trying to Upload Now!**")
            await message.reply_animation(magapylol, progress=progress_for_pyrogram, progress_args=("**Trying to Upload Now!** \n", download_msg, start_time))
            await download_msg.edit(f"**Successfully Uploaded** \n\n**Join @NexaBotsUpdates If You're Enjoying This Bot**")
            shutil.rmtree(basedir + "/" + userpath)
            return
        # Checking if it's a image
        if "image" in filemimespotted:
            await download_msg.edit("**Trying to Upload Now!**")
            await message.reply_photo(magapylol, progress=progress_for_pyrogram, progress_args=("**Trying to Upload Now!** \n", download_msg, start_time))
            await download_msg.edit(f"**Successfully Uploaded**")
        # Checking if it's a video
        elif "video" in filemimespotted:
            await download_msg.edit("`Generating Data...`")
            viddura = moviepy.editor.VideoFileClip(f"{magapylol}")
            vidduration = int(viddura.duration)
            thumbnail_path = f"{alreadylol}/thumbnail.jpg"
            subprocess.call(['ffmpeg', '-i', magapylol, '-ss', '00:00:00.000', '-vframes', '1', thumbnail_path])
            await message.reply_video(magapylol, duration=vidduration, thumb=thumbnail_path, progress=progress_for_pyrogram, progress_args=("**Trying to Upload Now!** \n", download_msg, start_time))
            await download_msg.edit(f"**Successfully Uploaded**")
        # Checking if it's a audio
        elif "audio" in filemimespotted:
            await download_msg.edit("**Trying to Upload Now!**")
            await message.reply_audio(magapylol, progress=progress_for_pyrogram, progress_args=("**Trying to Upload Now!** \n", download_msg, start_time))
            await download_msg.edit(f"**Successfully Uploaded**")
        # If it's not a image/video or audio it'll reply it as doc
        else:
            await download_msg.edit("**Trying to Upload Now!**")
            await message.reply_document(magapylol, progress=progress_for_pyrogram, progress_args=("**Trying to Upload Now!** \n", download_msg, start_time))
            await download_msg.edit(f"**Successfully Uploaded**")
    try:
        shutil.rmtree(basedir + "/" + userpath)
        print("Successfully Removed Downloaded File and the folder!")
    except Exception as e:
        await send_errors(e=e)
        return
