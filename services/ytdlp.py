from __future__ import annotations

import asyncio
import json
import logging
from pathlib import Path
from urllib.parse import urlparse

from utils.models import DownloadArtifact, DownloadOption, ParsedInput
from config import Settings
from services.progress import humanbytes
from utils.logging_config import redact_command, safe_url_label


VIDEO_EXTENSIONS = {"mp4", "mkv", "webm", "mov"}
AUDIO_EXTENSIONS = {"mp3", "m4a", "aac", "wav", "flac", "opus", "weba"}
logger = logging.getLogger(__name__)


def _command_base(parsed_input: ParsedInput, settings: Settings) -> list[str]:
    command = ["yt-dlp", "--no-warnings"]
    if settings.http_proxy:
        command.extend(["--proxy", settings.http_proxy])
    if parsed_input.username:
        command.extend(["--username", parsed_input.username])
    if parsed_input.password:
        command.extend(["--password", parsed_input.password])
    return command


async def _run_command(command: list[str], cwd: Path | None = None) -> tuple[str, str]:
    logger.debug("Running yt-dlp command | cwd=%s command=%s", cwd, redact_command(command))
    process = await asyncio.create_subprocess_exec(
        *command,
        cwd=str(cwd) if cwd else None,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    if process.returncode != 0:
        error_text = stderr.decode().strip() or stdout.decode().strip() or "yt-dlp failed"
        logger.warning(
            "yt-dlp command failed | cwd=%s command=%s error=%s",
            cwd,
            redact_command(command),
            error_text.splitlines()[0],
        )
        raise RuntimeError(error_text)
    return stdout.decode().strip(), stderr.decode().strip()


def _is_audio_only(format_note: str | None) -> bool:
    return bool(format_note and "audio only" in format_note.lower())


def _label_for_format(info: dict, format_data: dict, index: int) -> str:
    format_note = format_data.get("format_note") or format_data.get("format") or f"Format {index + 1}"
    size = format_data.get("filesize") or format_data.get("filesize_approx") or 0
    ext = format_data.get("ext", "")
    return f"Video {format_note} {ext} {humanbytes(size)}".strip()


def _ext_from_url(url: str) -> str | None:
    suffix = Path(urlparse(url).path).suffix
    return suffix.lstrip(".") if suffix else None


def _option_id(prefix: str, index: int) -> str:
    return f"{prefix}{index}"


async def probe_url(parsed_input: ParsedInput, settings: Settings) -> dict:
    command = _command_base(parsed_input, settings)
    command.extend(["--allow-dynamic-mpd", "--dump-single-json", parsed_input.source_url])
    logger.info("Probing source with yt-dlp | source=%s", safe_url_label(parsed_input.source_url))
    stdout, _ = await _run_command(command)
    if "\n" in stdout:
        stdout = stdout.splitlines()[0]
    payload = json.loads(stdout)
    logger.info(
        "Probe complete | source=%s title=%s extractor=%s",
        safe_url_label(parsed_input.source_url),
        payload.get("title", "-"),
        payload.get("extractor_key", payload.get("extractor", "-")),
    )
    return payload


def build_quick_youtube_options() -> list[DownloadOption]:
    return [
        DownloadOption(
            option_id="quick_audio",
            label="Audio",
            send_type="audio",
            mode="youtube_quick",
        ),
        DownloadOption(
            option_id="quick_video",
            label="Video",
            send_type="video",
            mode="youtube_quick",
        ),
    ]


def build_ytdlp_options(info: dict) -> list[DownloadOption]:
    options: list[DownloadOption] = []
    formats = info.get("formats") or []
    for index, format_data in enumerate(formats):
        format_note = format_data.get("format_note") or format_data.get("format")
        if format_note and "dash" in format_note.lower():
            continue
        if _is_audio_only(format_note):
            continue
        ext = format_data.get("ext")
        format_id = format_data.get("format_id")
        if not ext or not format_id:
            continue
        options.append(
            DownloadOption(
                option_id=_option_id("fmt", len(options)),
                label=_label_for_format(info, format_data, index),
                send_type="video",
                mode="ytdlp_format",
                format_id=str(format_id),
                file_ext=ext,
            )
        )

    if info.get("duration"):
        for quality in ("64k", "128k", "320k"):
            options.append(
                DownloadOption(
                    option_id=_option_id("audio", len(options)),
                    label=f"MP3 ({quality})",
                    send_type="audio",
                    mode="ytdlp_audio",
                    file_ext="mp3",
                    audio_quality=quality,
                )
            )
    return options


def build_direct_options(
    parsed_input: ParsedInput, info: dict | None = None
) -> list[DownloadOption]:
    ext = None
    source_url = parsed_input.source_url
    if info:
        ext = info.get("ext")
    if not ext:
        ext = _ext_from_url(source_url)

    send_type = "document"
    if ext and ext.lower() in VIDEO_EXTENSIONS:
        send_type = "video"
    elif ext and ext.lower() in AUDIO_EXTENSIONS:
        send_type = "audio"

    options = [
        DownloadOption(
            option_id="direct_primary",
            label="Send as media" if send_type != "document" else "Send as document",
            send_type=send_type,
            mode="direct",
            file_ext=ext,
        )
    ]
    if send_type != "document":
        options.append(
            DownloadOption(
                option_id="direct_document",
                label="Send as document",
                send_type="document",
                mode="direct",
                file_ext=ext,
            )
        )
    return options


def _pick_downloaded_file(work_dir: Path) -> Path:
    files = [
        path
        for path in work_dir.rglob("*")
        if path.is_file()
        and not path.name.endswith(".part")
        and path.suffix.lower() not in {".json", ".jpg", ".jpeg", ".png", ".webp"}
    ]
    if not files:
        discovered = sorted(
            str(path.relative_to(work_dir))
            for path in work_dir.rglob("*")
            if path.is_file()
        )
        logger.warning(
            "No downloaded media file found | work_dir=%s files=%s",
            work_dir,
            discovered,
        )
        raise RuntimeError("No file was downloaded")
    files.sort(key=lambda item: item.stat().st_mtime, reverse=True)
    return files[0]


def _caption_from_info(info: dict, fallback: str) -> str:
    title = info.get("title")
    webpage = info.get("webpage_url")
    if title and webpage:
        return f'<b><a href="{webpage}">{title}</a></b>'
    return title or fallback


async def download_quick_youtube(
    parsed_input: ParsedInput,
    option: DownloadOption,
    settings: Settings,
    work_dir: Path,
) -> DownloadArtifact:
    info = await probe_url(parsed_input, settings)
    work_dir = work_dir.resolve()
    work_dir.mkdir(parents=True, exist_ok=True)
    command = _command_base(parsed_input, settings)
    output_template = str(work_dir / "%(title)s [%(id)s].%(ext)s")

    if option.option_id == "quick_audio":
        command.extend(
            [
                "-f",
                "bestaudio",
                "--extract-audio",
                "--audio-format",
                "mp3",
                "-o",
                output_template,
                parsed_input.source_url,
            ]
        )
        send_type = "audio"
    else:
        command.extend(
            [
                "-f",
                "best[ext=mp4]/best",
                "-o",
                output_template,
                parsed_input.source_url,
            ]
        )
        send_type = "video"

    logger.info(
        "Starting quick YouTube download | source=%s mode=%s work_dir=%s",
        safe_url_label(parsed_input.source_url),
        option.option_id,
        work_dir,
    )
    await _run_command(command, cwd=work_dir)
    file_path = _pick_downloaded_file(work_dir)
    logger.info(
        "Quick YouTube download complete | file=%s bytes=%s send_type=%s",
        file_path.name,
        file_path.stat().st_size,
        send_type,
    )
    return DownloadArtifact(
        path=file_path,
        file_name=file_path.name,
        send_type=send_type,
        caption=_caption_from_info(info, file_path.stem),
    )


async def download_selected_format(
    parsed_input: ParsedInput,
    option: DownloadOption,
    info: dict,
    settings: Settings,
    work_dir: Path,
) -> DownloadArtifact:
    work_dir = work_dir.resolve()
    work_dir.mkdir(parents=True, exist_ok=True)
    command = _command_base(parsed_input, settings)
    output_template = str(work_dir / "%(title)s [%(id)s].%(ext)s")

    if option.mode == "ytdlp_audio":
        command.extend(
            [
                "--extract-audio",
                "--audio-format",
                option.file_ext or "mp3",
                "--audio-quality",
                option.audio_quality or "128k",
                "-o",
                output_template,
                parsed_input.source_url,
            ]
        )
        send_type = "audio"
    else:
        format_selector = option.format_id or "best"
        if "youtube" in parsed_input.source_url or "youtu.be" in parsed_input.source_url:
            format_selector = f"{format_selector}+bestaudio"
        command.extend(
            [
                "-f",
                format_selector,
                "--embed-subs",
                "-o",
                output_template,
                parsed_input.source_url,
            ]
        )
        send_type = option.send_type

    logger.info(
        "Starting yt-dlp format download | source=%s mode=%s format=%s send_type=%s work_dir=%s",
        safe_url_label(parsed_input.source_url),
        option.mode,
        option.format_id or option.audio_quality or option.file_ext or "-",
        send_type,
        work_dir,
    )
    await _run_command(command, cwd=work_dir)
    file_path = _pick_downloaded_file(work_dir)
    logger.info(
        "yt-dlp format download complete | file=%s bytes=%s send_type=%s",
        file_path.name,
        file_path.stat().st_size,
        send_type,
    )
    return DownloadArtifact(
        path=file_path,
        file_name=file_path.name,
        send_type=send_type,
        caption=_caption_from_info(info, file_path.stem),
    )
