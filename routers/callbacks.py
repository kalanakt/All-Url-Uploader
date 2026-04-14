from __future__ import annotations

import logging
from datetime import datetime

from aiogram import Router
from aiogram.types import CallbackQuery

from config import Settings
from routers.commands import handle_ui_callback
from services.direct_downloads import download_direct_file
from services.request_store import RequestStore
from services.thumbnail_store import ThumbnailStore
from services.telegram_uploads import upload_artifact
from services.ytdlp import download_quick_youtube, download_selected_format
from utils import text
from utils.callbacks import RequestCallback, UiCallback
from utils.logging_config import safe_url_label
from utils.models import DownloadOption, StoredRequest

router = Router(name="callbacks")
logger = logging.getLogger(__name__)


def _find_option(stored: StoredRequest, action: str) -> DownloadOption | None:
    for option in stored.options:
        if option.option_id == action:
            return option
    return None


@router.callback_query(UiCallback.filter())
async def ui_callback(query: CallbackQuery, callback_data: UiCallback) -> None:
    await handle_ui_callback(query, callback_data.action)


@router.callback_query(RequestCallback.filter())
async def request_callback(
    query: CallbackQuery,
    callback_data: RequestCallback,
    settings: Settings,
    request_store: RequestStore,
    thumbnail_store: ThumbnailStore,
) -> None:
    if not query.message:
        await query.answer()
        return

    stored = request_store.load(callback_data.token)
    if not stored:
        logger.warning(
            "Expired request callback | user=%s token=%s action=%s",
            query.from_user.id,
            callback_data.token,
            callback_data.action,
        )
        await query.message.edit_text(text.REQUEST_EXPIRED)
        await query.answer()
        return

    option = _find_option(stored, callback_data.action)
    if not option:
        logger.warning(
            "Unknown request option | user=%s token=%s action=%s",
            query.from_user.id,
            callback_data.token,
            callback_data.action,
        )
        await query.message.edit_text(text.REQUEST_EXPIRED)
        await query.answer()
        return

    started_at = datetime.now()
    work_dir = request_store.work_directory(stored.token)

    file_name = stored.parsed_input.custom_file_name or "downloaded-file"
    await query.message.edit_text(text.download_caption(file_name))
    logger.info(
        "Starting request action | user=%s token=%s type=%s option=%s send_type=%s source=%s",
        query.from_user.id,
        stored.token,
        stored.request_type,
        option.option_id,
        option.send_type,
        safe_url_label(stored.parsed_input.source_url),
    )

    try:
        if stored.request_type == "direct_download":
            artifact = await download_direct_file(
                status_message=query.message,
                parsed_input=stored.parsed_input,
                option=option,
                settings=settings,
                work_dir=work_dir,
                suggested_ext=stored.info.get("ext"),
            )
        elif stored.request_type == "youtube_quick":
            artifact = await download_quick_youtube(
                parsed_input=stored.parsed_input,
                option=option,
                settings=settings,
                work_dir=work_dir,
            )
        else:
            artifact = await download_selected_format(
                parsed_input=stored.parsed_input,
                option=option,
                info=stored.info,
                settings=settings,
                work_dir=work_dir,
            )

        await upload_artifact(
            bot=query.bot,
            status_message=query.message,
            source_message=query.message.reply_to_message or query.message,
            artifact=artifact,
            thumbnail_path=thumbnail_store.get(query.from_user.id),
            started_at=started_at,
        )
        logger.info(
            "Completed request action | user=%s token=%s file=%s send_type=%s",
            query.from_user.id,
            stored.token,
            artifact.file_name,
            artifact.send_type,
        )
    except Exception as exc:  # pylint: disable=broad-exception-caught  # pragma: no cover - user-facing safety boundary
        logger.exception(
            "Request action failed | user=%s token=%s type=%s option=%s",
            query.from_user.id,
            stored.token,
            stored.request_type,
            option.option_id,
        )
        await query.message.edit_text(f"{text.DOWNLOAD_FAILED}\n<code>{exc}</code>")
    finally:
        request_store.delete(stored.token)
        logger.info("Cleaned request state | token=%s", stored.token)
        await query.answer()
