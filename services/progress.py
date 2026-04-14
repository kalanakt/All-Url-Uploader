from __future__ import annotations

import math
import time


def humanbytes(size: int | float | None) -> str:
    if not size:
        return "0 B"
    power = 2**10
    units = {0: "B", 1: "KB", 2: "MB", 3: "GB", 4: "TB"}
    n = 0
    value = float(size)
    while value >= power and n < 4:
        value /= power
        n += 1
    return f"{value:.2f} {units[n]}"


def format_duration(seconds: int) -> str:
    minutes, sec = divmod(max(seconds, 0), 60)
    hours, minutes = divmod(minutes, 60)
    parts: list[str] = []
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    parts.append(f"{sec}s")
    return " ".join(parts)


def format_download_progress(
    file_name: str,
    downloaded: int,
    total: int,
    started_at: float,
) -> str:
    elapsed = max(time.time() - started_at, 1e-6)
    percentage = min(downloaded / total, 1) if total else 0
    bars = math.floor(percentage * 20)
    speed = downloaded / elapsed
    eta = int((total - downloaded) / speed) if speed and total else 0
    return (
        f"Downloading <b>{file_name}</b>\n\n"
        f"[{'#' * bars}{'.' * (20 - bars)}] {percentage * 100:.1f}%\n"
        f"{humanbytes(downloaded)} of {humanbytes(total)}\n"
        f"Speed: {humanbytes(speed)}/s\n"
        f"ETA: {format_duration(eta)}"
    )
