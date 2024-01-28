import logging
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)


async def Mdata01(download_directory):
    """
    Extract metadata information for video files.

    Parameters:
    - download_directory (str): The path to the video file.

    Returns:
    Tuple[int, int, int]: Tuple containing width, height, and duration.
    """
    width = 0
    height = 0
    duration = 0
    metadata = extractMetadata(createParser(download_directory))
    if metadata is not None:
        if metadata.has("duration"):
            duration = metadata.get("duration").seconds
        if metadata.has("width"):
            width = metadata.get("width")
        if metadata.has("height"):
            height = metadata.get("height")

    return width, height, duration


async def Mdata02(download_directory):
    """
    Extract metadata information for video files.

    Parameters:
    - download_directory (str): The path to the video file.

    Returns:
    Tuple[int, int]: Tuple containing width and duration.
    """
    width = 0
    duration = 0
    metadata = extractMetadata(createParser(download_directory))
    if metadata is not None:
        if metadata.has("duration"):
            duration = metadata.get("duration").seconds
        if metadata.has("width"):
            width = metadata.get("width")

    return width, duration


async def Mdata03(download_directory):
    """
    Extract metadata information for audio files.

    Parameters:
    - download_directory (str): The path to the audio file.

    Returns:
    int: Duration of the audio file.
    """
    metadata = extractMetadata(createParser(download_directory))
    return (
        metadata.get("duration").seconds
        if metadata is not None and metadata.has("duration")
        else 0
    )
