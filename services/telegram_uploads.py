import asyncio
import logging
import math
import os
import time
from datetime import datetime

from aiogram import Bot
from aiogram.types import FSInputFile, Message
from aiogram.utils.chat_action import ChatActionSender

from services.media import audio_duration, video_metadata, video_note_metadata
from services.progress import format_duration, humanbytes
from utils import text
from utils.models import DownloadArtifact


logger = logging.getLogger(__name__)


def _thumb_file(path: str | None) -> FSInputFile | None:
    if path and os.path.isfile(path):
        return FSInputFile(path)
    return None


async def _update_upload_status(
    status_message: Message,
    file_name: str,
    file_size: int,
) -> None:
    def get_tx_bytes() -> int:
        try:
            with open("/proc/net/dev", "r") as f:
                lines = f.readlines()
            total_tx = 0
            for line in lines:
                if ":" not in line:
                    continue
                parts = line.split(":")
                iface = parts[0].strip()
                if iface == "lo":
                    continue
                data_parts = parts[1].split()
                if len(data_parts) >= 9:
                    total_tx += int(data_parts[8])
            return total_tx
        except Exception:
            return 0

    started_at = time.time()
    start_tx = get_tx_bytes()
    last_tx = start_tx
    last_time = started_at
    smoothed_speed = 0.0
    alpha = 0.3  # EMA smoothing factor

    try:
        while True:
            await asyncio.sleep(2)
            current_time = time.time()
            current_tx = get_tx_bytes()

            # Fallback for systems that don't output proc tx stats (e.g. during local tests)
            if start_tx == 0 or current_tx == 0:
                elapsed = int(current_time - started_at)
                elapsed_str = format_duration(elapsed)
                text_caption = (
                    f"📤 <b>Uploading to Telegram</b>\n\n"
                    f"📝 <b>File:</b> <code>{file_name}</code>\n"
                    f"📦 <b>Size:</b> <code>{humanbytes(file_size)}</code>\n"
                    f"⏱️ <b>Time Elapsed:</b> <code>{elapsed_str}</code>\n\n"
                    f"⚡ <i>Sending media to cloud storage... Please wait.</i>"
                )
            else:
                elapsed_seconds = max(current_time - started_at, 1e-6)
                interval_seconds = max(current_time - last_time, 1e-6)

                # Find bytes sent in this interval
                interval_bytes = max(current_tx - last_tx, 0)
                instant_speed = interval_bytes / interval_seconds

                if smoothed_speed == 0.0:
                    smoothed_speed = instant_speed
                else:
                    smoothed_speed = alpha * instant_speed + (1 - alpha) * smoothed_speed

                uploaded_bytes = min(max(current_tx - start_tx, 0), file_size)
                percentage = uploaded_bytes / file_size if file_size else 0
                bars = math.floor(percentage * 20)

                remaining_bytes = max(file_size - uploaded_bytes, 0)
                eta = int(remaining_bytes / smoothed_speed) if smoothed_speed > 1024 else 0

                percentage_str = f"{percentage * 100:.1f}%"
                speed_str = f"{humanbytes(smoothed_speed)}/s"
                eta_str = format_duration(eta) if eta else "Calculating..."

                text_caption = (
                    f"📤 <b>Uploading to Telegram</b>\n\n"
                    f"📝 <b>File:</b> <code>{file_name}</code>\n"
                    f"[{'#' * bars}{'.' * (20 - bars)}] {percentage_str}\n"
                    f"{humanbytes(uploaded_bytes)} of {humanbytes(file_size)}\n"
                    f"Speed: {speed_str}\n"
                    f"ETA: {eta_str}\n\n"
                    f"⚡ <i>Sending media to cloud storage... Please wait.</i>"
                )

                last_tx = current_tx
                last_time = current_time

            try:
                await status_message.edit_text(text_caption)
            except Exception:
                pass
    except asyncio.CancelledError:
        pass


async def upload_artifact(
    *,
    bot: Bot,
    status_message: Message,
    source_message: Message,
    artifact: DownloadArtifact,
    thumbnail_path: str | None,
    started_at: datetime,
) -> None:
    await status_message.edit_text(text.upload_caption(artifact.file_name))
    thumb = _thumb_file(thumbnail_path)
    file_input = FSInputFile(artifact.path)
    download_seconds = int((datetime.now() - started_at).total_seconds())

    file_size = artifact.path.stat().st_size if artifact.path.exists() else 0
    max_size = 2000 * 1024 * 1024  # 2GB local Telegram Bot API upload limit
    if file_size > max_size:
        logger.warning(
            "File too large for Telegram upload | file=%s size=%s max=%s",
            artifact.file_name,
            file_size,
            max_size,
        )
        await status_message.edit_text(
            text.FILE_TOO_LARGE.format(
                seconds=download_seconds,
                size=humanbytes(file_size),
            )
        )
        artifact.path.unlink(missing_ok=True)
        return

    upload_started = datetime.now()
    logger.info(
        "Upload starting | chat=%s file=%s send_type=%s size=%s thumbnail=%s",
        source_message.chat.id,
        artifact.file_name,
        artifact.send_type,
        file_size,
        "yes" if thumb else "no",
    )

    # Start premium live uploading status updates
    updater_task = asyncio.create_task(
        _update_upload_status(status_message, artifact.file_name, file_size)
    )

    try:
        if artifact.send_type == "video":
            width, height, duration = video_metadata(artifact.path)
            async with ChatActionSender.upload_video(bot=bot, chat_id=source_message.chat.id):
                await source_message.reply_video(
                    video=file_input,
                    caption=artifact.caption,
                    duration=duration,
                    width=width,
                    height=height,
                    supports_streaming=True,
                    thumbnail=thumb,
                )
        elif artifact.send_type == "audio":
            duration = audio_duration(artifact.path)
            async with ChatActionSender.upload_document(bot=bot, chat_id=source_message.chat.id):
                await source_message.reply_audio(
                    audio=file_input,
                    caption=artifact.caption,
                    duration=duration,
                    thumbnail=thumb,
                    title=artifact.file_name,
                )
        elif artifact.send_type == "video_note":
            length, duration = video_note_metadata(artifact.path)
            async with ChatActionSender.upload_video_note(
                bot=bot, chat_id=source_message.chat.id
            ):
                await source_message.reply_video_note(
                    video_note=file_input,
                    duration=duration,
                    length=length or 240,
                    thumbnail=thumb,
                )
        else:
            async with ChatActionSender.upload_document(bot=bot, chat_id=source_message.chat.id):
                await source_message.reply_document(
                    document=file_input,
                    caption=artifact.caption,
                    thumbnail=thumb,
                )
    finally:
        updater_task.cancel()
        try:
            await updater_task
        except Exception:
            pass

    upload_seconds = int((datetime.now() - upload_started).total_seconds())
    logger.info(
        "Upload complete | chat=%s file=%s send_type=%s download_seconds=%s upload_seconds=%s",
        source_message.chat.id,
        artifact.file_name,
        artifact.send_type,
        download_seconds,
        upload_seconds,
    )
    await status_message.edit_text(
        text.DONE.format(
            download_seconds=download_seconds,
            upload_seconds=upload_seconds,
        )
    )
    artifact.path.unlink(missing_ok=True)
