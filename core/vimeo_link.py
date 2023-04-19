import os
import re
import subprocess
from urllib.parse import urlparse
import requests

import vimeo_dl as vimeo

from config import Config

# Define a filter to match messages with direct download links


async def vimeo_link(client, message, uvew):
    # Get the URL from the message text
    url = message.text.strip()
    # Extract the video ID from the URL
    match = re.search(r'vimeo.com/(\d+)', url)
    if not match:
        print("Invalid Vimeo URL")
        return

    video_id = match[1]

    # Fetch video information from Vimeo's API
    api_url = f"https://api.vimeo.com/videos/{video_id}"
    headers = {"Authorization": "Bearer YOUR_ACCESS_TOKEN"}
    response = requests.get(api_url, headers=headers)
    if response.status_code != 200:
        print("Failed to fetch video information")
        return

    data = response.json()
    title = data.get("name", "vimeo_video")
    ext = data.get("download", {}).get("data", {}).get("mime_type", "").split("/")[-1]

    # Download the video and save it with the extracted title and file extension
    response = requests.get(url)
    with open(f"{title}.{ext}", "wb") as f:
        f.write(response.content)

    video = vimeo.new(url)
    best = video.getbest()
    filename = f'{video.title}.{best.extension}'
    filepath = f'{Config.DOWNLOAD_LOCATION}/{filename}'

    # Download the file using vimeo-dl
    vimeo.download(url, filepath=filepath)

    # Get the chat ID from the message
    chat_id = message.chat.id

    # Upload the downloaded file to Telegram

    with open(filepath, 'rb') as f:
        await client.send_video(chat_id, f, supports_streaming=True)

    # Delete the local file
    os.remove(filepath)
