from __future__ import annotations

import logging
import mimetypes
import time
from pathlib import Path
from urllib.parse import urlparse

import aiohttp
from aiogram.types import Message

from config import Settings
from services.progress import format_download_progress
from utils.logging_config import safe_url_label
from utils.models import DownloadArtifact, DownloadOption, ParsedInput


logger = logging.getLogger(__name__)


def _filename_from_url(url: str) -> str:
    parsed = urlparse(url)
    name = Path(parsed.path).name
    return name or "downloaded-file"


def _normalize_file_name(file_name: str, ext: str | None) -> str:
    if not ext:
        return file_name
    if file_name.lower().endswith(f".{ext.lower()}"):
        return file_name
    return f"{file_name}.{ext}"


def _progress_milestone(downloaded: int, total: int) -> int | None:
    if not total:
        return None
    milestone = int((downloaded / total) * 4) * 25
    return milestone if milestone in {25, 50, 75, 100} else None


async def download_direct_file(
    *,
    status_message: Message,
    parsed_input: ParsedInput,
    option: DownloadOption,
    settings: Settings,
    work_dir: Path,
    suggested_ext: str | None = None,
) -> DownloadArtifact:
    work_dir.mkdir(parents=True, exist_ok=True)
    file_name = parsed_input.custom_file_name or _filename_from_url(
        parsed_input.source_url
    )
    logger.info(
        "Direct download starting | source=%s send_type=%s work_dir=%s",
        safe_url_label(parsed_input.source_url),
        option.send_type,
        work_dir,
    )

    timeout = aiohttp.ClientTimeout(total=settings.process_max_timeout)
    connector = None
    if settings.http_proxy:
        connector = aiohttp.TCPConnector(ssl=False)

    async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
        async with session.get(parsed_input.source_url, proxy=settings.http_proxy or None) as response:
            response.raise_for_status()
            content_type = response.headers.get("Content-Type", "")
            ext = option.file_ext or suggested_ext
            if not ext:
                guessed_ext = mimetypes.guess_extension(
                    content_type.split(";")[0].strip()
                )
                ext = guessed_ext.lstrip(".") if guessed_ext else None

            file_name = _normalize_file_name(file_name, ext)
            destination = work_dir / file_name

            total = int(response.headers.get("Content-Length", "0") or "0")
            downloaded = 0
            started = time.time()
            last_update = 0.0
            logged_milestones: set[int] = set()

            with destination.open("wb") as handle:
                async for chunk in response.content.iter_chunked(settings.chunk_size):
                    handle.write(chunk)
                    downloaded += len(chunk)
                    now = time.time()
                    milestone = _progress_milestone(downloaded, total)
                    if milestone and milestone not in logged_milestones:
                        logged_milestones.add(milestone)
                        logger.info(
                            "Direct download progress | file=%s progress=%s%% downloaded=%s total=%s",
                            file_name,
                            milestone,
                            downloaded,
                            total,
                        )
                    if total and (now - last_update >= 2 or downloaded >= total):
                        await status_message.edit_text(
                            format_download_progress(
                                file_name=file_name,
                                downloaded=downloaded,
                                total=total,
                                started_at=started,
                            )
                        )
                        last_update = now

    caption = parsed_input.custom_file_name or file_name
    logger.info(
        "Direct download complete | file=%s bytes=%s destination=%s elapsed=%.1fs",
        file_name,
        destination.stat().st_size if destination.exists() else 0,
        destination,
        time.time() - started,
    )
    return DownloadArtifact(
        path=destination,
        file_name=file_name,
        send_type=option.send_type,
        caption=caption,
    )
