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
import json
import time
import shutil
import asyncio
import logging
import subprocess

from pyrogram.types import *
from datetime import datetime

from Uploader.utitles import *
if bool(os.environ.get("WEBHOOK")):
    from Uploader.config import Config
else:
    from sample_config import Config
from Uploader.script import Translation
from Uploader.functions.ran_text import random_char
from Uploader.functions.display_progress import progress_for_pyrogram, humanbytes

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def youtube_dl_call_back(bot, update):
    cb_data = update.data
    # youtube_dl extractors
    tg_send_type, youtube_dl_format, youtube_dl_ext, ranom = cb_data.split("|")
    print(cb_data)
    random1 = random_char(5)
    save_ytdl_json_path = Config.DOWNLOAD_LOCATION + \
        "/" + str(update.from_user.id) + f'{ranom}' + ".json"
    try:
        with open(save_ytdl_json_path, "r", encoding="utf8") as f:
            response_json = json.load(f)
    except (FileNotFoundError) as e:
        await update.message.delete()
        return False
    youtube_dl_url = update.message.reply_to_message.text
    custom_file_name = str(response_json.get("title")) + \
        "_" + youtube_dl_format + "." + youtube_dl_ext
    youtube_dl_username = None
    youtube_dl_password = None
    if "|" in youtube_dl_url:
        url_parts = youtube_dl_url.split("|")
        if len(url_parts) == 2:
            youtube_dl_url = url_parts[0]
            custom_file_name = url_parts[1]
        elif len(url_parts) == 4:
            youtube_dl_url = url_parts[0]
            custom_file_name = url_parts[1]
            youtube_dl_username = url_parts[2]
            youtube_dl_password = url_parts[3]
        else:
            for entity in update.message.reply_to_message.entities:
                if entity.type == "text_link":
                    youtube_dl_url = entity.url
                elif entity.type == "url":
                    o = entity.offset
                    l = entity.length
                    youtube_dl_url = youtube_dl_url[o:o + l]
        if youtube_dl_url is not None:
            youtube_dl_url = youtube_dl_url.strip()
        if custom_file_name is not None:
            custom_file_name = custom_file_name.strip()
        # https://stackoverflow.com/a/761825/4723940
        if youtube_dl_username is not None:
            youtube_dl_username = youtube_dl_username.strip()
        if youtube_dl_password is not None:
            youtube_dl_password = youtube_dl_password.strip()
        logger.info(youtube_dl_url)
        logger.info(custom_file_name)
    else:
        for entity in update.message.reply_to_message.entities:
            if entity.type == "text_link":
                youtube_dl_url = entity.url
            elif entity.type == "url":
                o = entity.offset
                l = entity.length
                youtube_dl_url = youtube_dl_url[o:o + l]
    await update.message.edit_caption(
        caption=Translation.DOWNLOAD_START.format(custom_file_name)

    )
    description = Translation.CUSTOM_CAPTION_UL_FILE
    if "fulltitle" in response_json:
        description = response_json["fulltitle"][:1021]
        # escape Markdown and special characters
    tmp_directory_for_each_user = Config.DOWNLOAD_LOCATION + \
        "/" + str(update.from_user.id) + f'{random1}'
    if not os.path.isdir(tmp_directory_for_each_user):
        os.makedirs(tmp_directory_for_each_user)
    download_directory = f"{tmp_directory_for_each_user}/{custom_file_name}"

    command_to_exec = []
    if tg_send_type == "audio":
        command_to_exec = [
            "yt-dlp",
            "-c",
            "--max-filesize", str(Config.TG_MAX_FILE_SIZE),
            "--bidi-workaround",
            "--extract-audio",
            "--audio-format", youtube_dl_ext,
            "--audio-quality", youtube_dl_format,
            youtube_dl_url,
            "-o", download_directory
        ]
    else:
        # command_to_exec = ["yt-dlp", "-f", youtube_dl_format, "--hls-prefer-ffmpeg", "--recode-video", "mp4", "-k", youtube_dl_url, "-o", download_directory]
        minus_f_format = youtube_dl_format
        if "youtu" in youtube_dl_url:
            minus_f_format = f"{youtube_dl_format}+bestaudio"
        command_to_exec = [
            "yt-dlp",
            "-c",
            "--max-filesize", str(Config.TG_MAX_FILE_SIZE),
            "--embed-subs",
            "-f", minus_f_format,
            "--bidi-workaround",
            youtube_dl_url,
            "-o", download_directory
        ]

    if Config.HTTP_PROXY != "":
        command_to_exec.append("--proxy")
        command_to_exec.append(Config.HTTP_PROXY)
    if youtube_dl_username is not None:
        command_to_exec.append("--username")
        command_to_exec.append(youtube_dl_username)
    if youtube_dl_password is not None:
        command_to_exec.append("--password")
        command_to_exec.append(youtube_dl_password)
    command_to_exec.append("--no-warnings")
    # command_to_exec.append("--quiet")
    logger.info(command_to_exec)
    start = datetime.now()
    process = await asyncio.create_subprocess_exec(
        *command_to_exec,
        # stdout must a pipe to be accessible as process.stdout
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    # Wait for the subprocess to finish
    stdout, stderr = await process.communicate()
    e_response = stderr.decode().strip()
    t_response = stdout.decode().strip()
    logger.info(e_response)
    logger.info(t_response)
    ad_string_to_replace = "please report this issue on https://github.com/kalanakt/All-Url-Uploader/issues"
    if e_response and ad_string_to_replace in e_response:
        error_message = e_response.replace(ad_string_to_replace, "")
        await update.message.edit_caption(

            text=error_message
        )
        return False

    if t_response:
        logger.info(t_response)
        try:
            os.remove(save_ytdl_json_path)
        except FileNotFoundError as exc:
            pass

        end_one = datetime.now()
        time_taken_for_download = (end_one - start).seconds
        file_size = Config.TG_MAX_FILE_SIZE + 1
        try:
            file_size = os.stat(download_directory).st_size
        except FileNotFoundError as exc:
            download_directory = os.path.splitext(
                download_directory)[0] + "." + "mkv"
            # https://stackoverflow.com/a/678242/4723940
            file_size = os.stat(download_directory).st_size

        download_location = f"{Config.DOWNLOAD_LOCATION}/{update.from_user.id}.jpg"
        thumb = download_location if os.path.isfile(
            download_location) else None

        if ((file_size > Config.TG_MAX_FILE_SIZE)):
            await update.message.edit_caption(

                caption=Translation.RCHD_TG_API_LIMIT.format(
                    time_taken_for_download, humanbytes(file_size))

            )
        else:
            await update.message.edit_caption(
                caption=Translation.UPLOAD_START.format(custom_file_name)

            )
            start_time = time.time()
            if tg_send_type == "video":
                width, height, duration = await Mdata01(download_directory)
                await update.message.reply_video(
                    # chat_id=update.message.chat.id,
                    video=download_directory,
                    caption=description,
                    duration=duration,
                    width=width,
                    height=height,
                    supports_streaming=True,
                    thumb=thumb,
                    # reply_to_message_id=update.id,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        Translation.UPLOAD_START,
                        update.message,
                        start_time
                    )
                )
            elif tg_send_type == "audio":
                duration = await Mdata03(download_directory)
                await update.message.reply_audio(
                    # chat_id=update.message.chat.id,
                    audio=download_directory,
                    caption=description,
                    duration=duration,
                    thumb=thumb,
                    # reply_to_message_id=update.id,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        Translation.UPLOAD_START,
                        update.message,
                        start_time
                    )
                )
            elif tg_send_type == "vm":
                width, duration = await Mdata02(download_directory)
                await update.message.reply_video_note(
                    # chat_id=update.message.chat.id,
                    video_note=download_directory,
                    duration=duration,
                    length=width,
                    thumb=thumb,
                    # reply_to_message_id=update.id,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        Translation.UPLOAD_START,
                        update.message,
                        start_time
                    )
                )
            else:
                await update.message.reply_document(
                    # chat_id=update.message.chat.id,
                    document=download_directory,
                    caption=description,
                    # parse_mode=enums.ParseMode.HTML,
                    # reply_to_message_id=update.id,
                    thumb=thumb,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        Translation.UPLOAD_START,
                        update.message,
                        start_time
                    )
                )

            end_two = datetime.now()
            time_taken_for_upload = (end_two - end_one).seconds
            try:
                shutil.rmtree(tmp_directory_for_each_user)
            except Exception:
                pass
            await update.message.edit_caption(
                caption=Translation.AFTER_SUCCESSFUL_UPLOAD_MSG_WITH_TS.format(
                    time_taken_for_download, time_taken_for_upload)

            )

            logger.info(f"Downloaded in: {str(time_taken_for_download)}")
            logger.info(f"Uploaded in: {str(time_taken_for_upload)}")
