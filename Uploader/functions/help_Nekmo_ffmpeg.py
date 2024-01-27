import os
import asyncio
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata
import time
import logging

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def place_water_mark(input_file, output_file, water_mark_file):
    """
    Place a watermark on the input file and save the result to the output file.

    Parameters:
    - input_file (str): Path to the input file.
    - output_file (str): Path to save the output file.
    - water_mark_file (str): Path to the watermark file.

    Returns:
    str: Path to the watermarked output file.
    """
    watermarked_file = f"{output_file}.watermark.png"
    metadata = extractMetadata(createParser(input_file))
    width = metadata.get("width")
    # Command to shrink the watermark file
    shrink_watermark_file_genertor_command = [
        "ffmpeg",
        "-i",
        water_mark_file,
        "-y -v quiet",
        "-vf",
        f"scale={width}*0.5:-1",
        watermarked_file,
    ]

    process = await asyncio.create_subprocess_exec(
        *shrink_watermark_file_genertor_command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    stderr.decode().strip()
    stdout.decode().strip()

    # Command to overlay the watermark on the input file
    commands_to_execute = [
        "ffmpeg",
        "-i",
        input_file,
        "-i",
        watermarked_file,
        "-filter_complex",
        '"overlay=(main_w-overlay_w):(main_h-overlay_h)"',
        output_file,
    ]
    process = await asyncio.create_subprocess_exec(
        *commands_to_execute,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    stderr.decode().strip()
    stdout.decode().strip()
    return output_file


async def take_screen_shot(video_file, output_directory, ttl):
    """
    Take a screenshot from a video file at a specified time and save it to the output directory.

    Parameters:
    - video_file (str): Path to the video file.
    - output_directory (str): Directory to save the screenshot.
    - ttl (int): Time to take the screenshot in seconds.

    Returns:
    str: Path to the saved screenshot file.
    """
    out_put_file_name = output_directory + "/" + str(time.time()) + ".jpg"
    file_genertor_command = [
        "ffmpeg",
        "-ss",
        str(ttl),
        "-i",
        video_file,
        "-vframes",
        "1",
        out_put_file_name,
    ]
    process = await asyncio.create_subprocess_exec(
        *file_genertor_command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    stderr.decode().strip()
    stdout.decode().strip()
    return out_put_file_name if os.path.lexists(out_put_file_name) else None


async def cult_small_video(video_file, output_directory, start_time, end_time):
    """
    Cut a small portion of a video file and save it to the output directory.

    Parameters:
    - video_file (str): Path to the video file.
    - output_directory (str): Directory to save the cut video.
    - start_time (int): Start time of the cut in seconds.
    - end_time (int): End time of the cut in seconds.

    Returns:
    str: Path to the saved cut video file.
    """
    out_put_file_name = output_directory + "/" + str(round(time.time())) + ".mp4"
    file_genertor_command = [
        "ffmpeg",
        "-i",
        video_file,
        "-ss",
        start_time,
        "-to",
        end_time,
        "-async",
        "1",
        "-strict",
        "-2",
        out_put_file_name,
    ]
    process = await asyncio.create_subprocess_exec(
        *file_genertor_command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    stderr.decode().strip()
    stdout.decode().strip()
    return out_put_file_name if os.path.lexists(out_put_file_name) else None


async def generate_screen_shots(
    video_file, output_directory, is_watermarkable, wf, min_duration, no_of_photos
):
    """
    Generate screen shots from a video file and optionally apply a watermark.

    Parameters:
    - video_file (str): Path to the video file.
    - output_directory (str): Directory to save the screen shots.
    - is_watermarkable (bool): Whether to apply a watermark.
    - wf (str): Path to the watermark file.
    - min_duration (int): Minimum duration of the video to generate screen shots.
    - no_of_photos (int): Number of screen shots to generate.

    Returns:
    List[str]: List of paths to the generated screen shots.
    """
    metadata = extractMetadata(createParser(video_file))
    duration = 0
    if metadata is not None and metadata.has("duration"):
        duration = metadata.get("duration").seconds
    if duration > min_duration:
        images = []
        ttl_step = duration // no_of_photos
        current_ttl = ttl_step
        for _ in range(no_of_photos):
            ss_img = await take_screen_shot(video_file, output_directory, current_ttl)
            current_ttl = current_ttl + ttl_step
            if is_watermarkable:
                ss_img = await place_water_mark(
                    ss_img, f"{output_directory}/{str(time.time())}.jpg", wf
                )
            images.append(ss_img)
        return images

    return None
