from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from routers.callbacks import request_callback
from routers.commands import about_command, help_command, start_command
from routers.intake import intake_message
from routers.thumbnails import delete_thumbnail, show_thumbnail
from services.cooldown import CooldownManager
from services.request_store import RequestStore
from services.thumbnail_store import ThumbnailStore
from services.ytdlp import _pick_downloaded_file
from tests.conftest import make_message, make_settings
from utils.callbacks import RequestCallback
from utils.models import DownloadOption, ParsedInput, StoredRequest


@pytest.mark.asyncio
async def test_start_help_about_handlers():
    message = make_message()

    await start_command(message)
    await help_command(message)
    await about_command(message)

    assert message.answer.await_count == 3


@pytest.mark.asyncio
async def test_thumbnail_handlers(tmp_path):
    store = ThumbnailStore(tmp_path / "thumbs")
    message = make_message()

    await show_thumbnail(message, store)
    assert message.answer.await_args_list[0].args[0].startswith("You do not have")

    thumbnail = store.path_for_user(message.from_user.id)
    thumbnail.write_bytes(b"jpg")

    await delete_thumbnail(message, store)
    assert message.answer.await_args_list[-1].args[0].startswith("Your thumbnail")


@pytest.mark.asyncio
async def test_intake_message_builds_quick_youtube_keyboard(tmp_path):
    settings = make_settings(tmp_path)
    settings.ensure_directories()
    store = RequestStore(settings.requests_dir, settings.work_dir)
    cooldown = CooldownManager(timeout_seconds=60)

    message = make_message()
    message.text = "https://youtu.be/example"
    status_message = SimpleNamespace(edit_text=AsyncMock())
    message.reply.return_value = status_message

    await intake_message(message, settings, cooldown, store)

    message.reply.assert_awaited_once()
    status_message.edit_text.assert_awaited_once()


@pytest.mark.asyncio
async def test_request_callback_uses_stored_request(monkeypatch, tmp_path):
    settings = make_settings(tmp_path)
    settings.ensure_directories()
    store = RequestStore(settings.requests_dir, settings.work_dir)
    thumbnails = ThumbnailStore(settings.thumbnails_dir)
    stored = StoredRequest(
        token="token123",
        request_type="direct_download",
        parsed_input=ParsedInput(source_url="https://example.com/file.mp4"),
        options=[
            DownloadOption(
                option_id="direct_primary",
                label="Send as media",
                send_type="video",
                mode="direct",
                file_ext="mp4",
            )
        ],
        info={"ext": "mp4"},
    )
    store.save(stored)

    artifact = SimpleNamespace(
        path=tmp_path / "video.mp4",
        file_name="video.mp4",
        send_type="video",
        caption="video",
    )
    artifact.path.write_bytes(b"video")
    download_mock = AsyncMock(return_value=artifact)
    upload_mock = AsyncMock()
    monkeypatch.setattr(
        "routers.callbacks.download_direct_file",
        download_mock,
    )
    monkeypatch.setattr(
        "routers.callbacks.upload_artifact",
        upload_mock,
    )

    source_message = SimpleNamespace(chat=SimpleNamespace(id=500))
    status_message = SimpleNamespace(
        edit_text=AsyncMock(),
        reply_to_message=source_message,
    )
    query = SimpleNamespace(
        message=status_message,
        from_user=SimpleNamespace(id=99),
        bot=SimpleNamespace(),
        answer=AsyncMock(),
    )

    await request_callback(
        query,
        RequestCallback(token="token123", action="direct_primary"),
        settings,
        store,
        thumbnails,
    )

    download_mock.assert_awaited_once()
    upload_mock.assert_awaited_once()


def test_pick_downloaded_file_finds_nested_media(tmp_path):
    work_dir = tmp_path / "work"
    nested = work_dir / "nested"
    nested.mkdir(parents=True)
    media = nested / "clip.mp3"
    media.write_bytes(b"audio")
    (work_dir / "info.json").write_text("{}", encoding="utf-8")

    selected = _pick_downloaded_file(work_dir)

    assert selected == media
