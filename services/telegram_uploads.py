from __future__ import annotations

import logging
import os
from datetime import datetime

from aiogram import Bot
from aiogram.types import FSInputFile, Message
from aiogram.utils.chat_action import ChatActionSender

from services.media import audio_duration, video_metadata, video_note_metadata
from services.progress import humanbytes
from utils import text
from utils.models import DownloadArtifact


logger = logging.getLogger(__name__)


def _thumb_file(path: str | None) -> FSInputFile | None:
    if path and os.path.isfile(path):
        return FSInputFile(path)
    return None


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
