# MIT License

# Copyright (c) 2022 Hash Minner

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE

import os
import time
import aiohttp
import asyncio
import logging

from datetime import datetime

from Uploader.functions.display_progress import progress_for_pyrogram, humanbytes, TimeFormatter
from Uploader.utitles import *
from Uploader.script import Translation

import logging

from config import Config
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

logging.getLogger("pyrogram").setLevel(logging.WARNING)


async def ddl_call_back(bot, update):  # sourcery skip: low-code-quality
    cb_data = update.data
    tg_send_type, youtube_dl_format, youtube_dl_ext = cb_data.split("=")
    youtube_dl_url = update.message.reply_to_message.text
    custom_file_name = os.path.basename(youtube_dl_url)
    if " " in youtube_dl_url:
        url_parts = youtube_dl_url.split(" * ")
        if len(url_parts) == 2:
            youtube_dl_url = url_parts[0]
            custom_file_name = url_parts[1]
        else:
            for entity in update.message.reply_to_message.entities:
                if entity.type == "text_link":
                    youtube_dl_url = entity.url
                elif entity.type == "url":
                    o = entity.offset
                    youtube_dl_url = youtube_dl_url[o:o + entity.length]
        if youtube_dl_url is not None:
            youtube_dl_url = youtube_dl_url.strip()
        if custom_file_name is not None:
            custom_file_name = custom_file_name.strip()
    else:
        for entity in update.message.reply_to_message.entities:
            if entity.type == "text_link":
                youtube_dl_url = entity.url
            elif entity.type == "url":
                o = entity.offset
                l = entity.length
                youtube_dl_url = youtube_dl_url[o:o + l]
    description = custom_file_name
    if f".{youtube_dl_ext}" not in custom_file_name:
        custom_file_name += f'.{youtube_dl_ext}'
    logger.info(youtube_dl_url)
    logger.info(custom_file_name)
    start = datetime.now()
    await bot.edit_message_text(text=Translation.DOWNLOAD_START.format(custom_file_name), chat_id=update.message.chat.id, message_id=update.message.id)

    tmp_directory_for_each_user = f"{Config.DOWNLOAD_LOCATION}/{str(update.from_user.id)}"

    if not os.path.isdir(tmp_directory_for_each_user):
        os.makedirs(tmp_directory_for_each_user)
    download_directory = f"{tmp_directory_for_each_user}/{custom_file_name}"
    command_to_exec = []
    async with aiohttp.ClientSession() as session:
        c_time = time.time()
        try:
            await download_coroutine(bot, session, youtube_dl_url, download_directory, update.message.chat.id, update.message.id, c_time)

        except asyncio.TimeoutError:
            await bot.edit_message_text(text=Translation.SLOW_URL_DECED, chat_id=update.message.chat.id, message_id=update.message.id)

            return False
    if os.path.exists(download_directory):
        save_ytdl_json_path = f"{Config.DOWNLOAD_LOCATION}/{str(update.message.chat.id)}.json"
        download_location = f"{Config.DOWNLOAD_LOCATION}/{update.from_user.id}.jpg"
        thumb = download_location if os.path.isfile(
            download_location) else None

        if os.path.exists(save_ytdl_json_path):
            os.remove(save_ytdl_json_path)
        end_one = datetime.now()
        await bot.edit_message_text(text=Translation.UPLOAD_START, chat_id=update.message.chat.id, message_id=update.message.id)

        file_size = Config.TG_MAX_FILE_SIZE + 1
        try:
            file_size = os.stat(download_directory).st_size
        except FileNotFoundError as exc:
            download_directory = f"{os.path.splitext(download_directory)[0]}.mkv"
            file_size = os.stat(download_directory).st_size
        if file_size > Config.TG_MAX_FILE_SIZE:
            await bot.edit_message_text(chat_id=update.message.chat.id, text=Translation.RCHD_TG_API_LIMIT, message_id=update.message.id)

        else:
            start_time = time.time()
            if tg_send_type == "video":
                width, height, duration = await Mdata01(download_directory)
                await bot.send_video(chat_id=update.message.chat.id, video=download_directory, thumb=thumb, caption=description, duration=duration, width=width, height=height, supports_streaming=True, reply_to_message_id=update.message.reply_to_message.id, progress=progress_for_pyrogram, progress_args=(Translation.UPLOAD_START, update.message, start_time))

            elif tg_send_type == "audio":
                duration = await Mdata03(download_directory)
                await bot.send_audio(chat_id=update.message.chat.id, audio=download_directory, thumb=thumb, caption=description, duration=duration, reply_to_message_id=update.message.reply_to_message.id, progress=progress_for_pyrogram, progress_args=(Translation.UPLOAD_START, update.message, start_time))

            elif tg_send_type == "vm":
                width, duration = await Mdata02(download_directory)
                await bot.send_video_note(chat_id=update.message.chat.id, video_note=download_directory, thumb=thumb, duration=duration, length=width, reply_to_message_id=update.message.reply_to_message.id, progress=progress_for_pyrogram, progress_args=(Translation.UPLOAD_START, update.message, start_time))

            else:
                await bot.send_document(chat_id=update.message.chat.id, document=download_directory, thumb=thumb, caption=description, reply_to_message_id=update.message.reply_to_message.id, progress=progress_for_pyrogram, progress_args=(Translation.UPLOAD_START, update.message, start_time))

            end_two = datetime.now()
            try:
                os.remove(download_directory)
            except Exception:
                pass
            time_taken_for_download = (end_one - start).seconds
            time_taken_for_upload = (end_two - end_one).seconds
            await bot.edit_message_text(text=Translation.AFTER_SUCCESSFUL_UPLOAD_MSG_WITH_TS.format(time_taken_for_download, time_taken_for_upload), chat_id=update.message.chat.id, message_id=update.message.id, disable_web_page_preview=True)

            logger.info(f"Downloaded in: {str(time_taken_for_download)}")
            logger.info(f"Uploaded in: {str(time_taken_for_upload)}")
    else:
        await bot.edit_message_text(text=Translation.NO_VOID_FORMAT_FOUND.format("Incorrect Link"), chat_id=update.message.chat.id, message_id=update.message.id, disable_web_page_preview=True)


async def download_coroutine(bot, session, url, file_name, chat_id, message_id, start):
    downloaded = 0
    display_message = ""
    async with session.get(url, timeout=Config.PROCESS_MAX_TIMEOUT) as response:
        total_length = int(response.headers["Content-Length"])
        content_type = response.headers["Content-Type"]
        if "text" in content_type and total_length < 500:
            return await response.release()
        with open(file_name, "wb") as f_handle:
            while True:
                chunk = await response.content.read(Config.CHUNK_SIZE)
                if not chunk:
                    break
                f_handle.write(chunk)
                downloaded += Config.CHUNK_SIZE
                now = time.time()
                diff = now - start
                if round(diff % 5.0) == 0 or downloaded == total_length:
                    percentage = downloaded * 100 / total_length
                    speed = downloaded / diff
                    elapsed_time = round(diff) * 1000
                    time_to_completion = (
                        round((total_length - downloaded) / speed) * 1000)
                    estimated_total_time = elapsed_time + time_to_completion
                    try:
                        current_message = """**Download Status**
URL: {}
File Size: {}
Downloaded: {}
ETA: {}""".format(url, humanbytes(total_length), humanbytes(downloaded), TimeFormatter(estimated_total_time))

                        if current_message != display_message:
                            await bot.edit_message_text(chat_id, message_id, text=current_message)
                            display_message = current_message
                    except Exception as e:
                        logger.info(str(e))
        return await response.release()
