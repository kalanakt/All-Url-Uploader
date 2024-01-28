import logging
import os
import time
import requests

from plugins.functions.display_progress import humanbytes

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def DetectFileSize(url):
    """
    Detect the file size of a remote file by sending a HEAD request.

    Parameters:
    - url (str): URL of the remote file.

    Returns:
    int: Size of the file in bytes.
    """
    r = requests.head(url, allow_redirects=True, timeout=60)
    return int(r.headers.get("content-length", 0))


def DownLoadFile(url, file_name, chunk_size, client, ud_type, message_id, chat_id):
    """
    Download a file from a given URL and display the download progress.

    Parameters:
    - url (str): URL of the file to be downloaded.
    - file_name (str): Path to save the downloaded file.
    - chunk_size (int): Size of each download chunk.
    - client: Pyrogram client (optional).
    - ud_type (str): Type of the download (e.g., "File", "Video").
    - message_id: ID of the message to update the download progress.
    - chat_id: ID of the chat to update the download progress.

    Returns:
    str: Path to the downloaded file.
    """
    if os.path.exists(file_name):
        os.remove(file_name)
    if not url:
        return file_name

    r = requests.get(url, allow_redirects=True, stream=True)
    total_size = int(r.headers.get("content-length", 0))
    downloaded_size = 0

    with open(file_name, "wb") as fd:
        for chunk in r.iter_content(chunk_size=chunk_size):
            if chunk:
                fd.write(chunk)
                downloaded_size += chunk_size

            if client is not None and ((total_size // downloaded_size) % 5) == 0:
                time.sleep(0.3)
                try:
                    client.edit_message_text(
                        chat_id,
                        message_id,
                        text=f"{ud_type}: {humanbytes(downloaded_size)} of {humanbytes(total_size)}",
                    )
                except Exception as e:
                    logger.info(f"Error: {e}")
                    return

    return file_name
