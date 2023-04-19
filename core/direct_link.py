import os
import subprocess
from urllib.parse import urlparse

import youtube_dl

from config import Config


# Define a filter to match messages with direct download links
async def direct_link(client, message, uvew):
    # Get the URL from the message text
    url = message.text.strip()

    # progress bar
    async def progress_hook(d):
        await uvew.edit_text(f"Downloading your Video : {int(d['downloaded_bytes']*100/d['total_bytes'])} %")

    # Download the file using youtube-dl
    ydl_opts = {
        'outtmpl': f'{Config.DOWNLOAD_LOCATION}/%(title)s.%(ext)s',
        'nooverwrites': True,
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',
        'progress_hooks': [progress_hook],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            info_dict = ydl.extract_info(url, download=True)
        except youtube_dl.DownloadError:
            await message.reply_text('Failed to download file')
            return

    # Get the chat ID from the message
    chat_id = message.chat.id

    # Check if the filename key exists in the info_dict
    if 'webpage_url_basename' not in info_dict:
        await message.reply_text('Failed to download file')
        return

    file_directly = Config.DOWNLOAD_LOCATION + \
        '/' + info_dict['webpage_url_basename']

    # Upload the downloaded file to Telegram

    with open(file_directly, 'rb') as f:
        await client.send_video(chat_id, f, supports_streaming=True)

    # Delete the local file
    os.remove(file_directly)
