import os
import logging
from urllib.parse import urlparse

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def get_file_extension_from_url(url):
    """
    Get the file extension from a URL.

    Parameters:
    - url (str): URL of the file.

    Returns:
    str: File extension.
    """
    url_path = urlparse(url).path
    basename = os.path.basename(url_path)
    return basename.split(".")[-1]


def get_resolution(info_dict):
    """
    Get the width and height of a video from its info dictionary.

    Parameters:
    - info_dict (dict): Dictionary containing information about the video.

    Returns:
    tuple: Width and height of the video.
    """
    width = 0
    height = 0

    if {"width", "height"} <= info_dict.keys():
        width = int(info_dict["width"])
        height = int(info_dict["height"])
    # https://support.google.com/youtube/answer/6375112
    elif info_dict["height"] == 1080:
        width = 1920
        height = 1080
    elif info_dict["height"] == 720:
        width = 1280
        height = 720
    elif info_dict["height"] == 480:
        width = 854
        height = 480
    elif info_dict["height"] == 360:
        width = 640
        height = 360
    elif info_dict["height"] == 240:
        width = 426
        height = 240
    return width, height
