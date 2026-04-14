from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


def _parse_int_set(raw_value: str | None) -> set[int]:
    if not raw_value:
        return set()
    values: set[int] = set()
    for chunk in raw_value.replace(",", " ").split():
        if chunk:
            values.add(int(chunk))
    return values


def _parse_chunk_size(raw_value: str | None) -> int:
    size = int(raw_value or "128")
    return size * 1024 if size < 1024 else size


@dataclass(slots=True)
class Settings:
    bot_token: str
    owner_id: int
    auth_users: set[int]
    download_location: Path
    chunk_size: int
    http_proxy: str
    process_max_timeout: int

    @classmethod
    def from_env(cls) -> "Settings":
        load_dotenv()

        bot_token = os.environ.get("BOT_TOKEN", "").strip()
        owner_id = int(os.environ.get("OWNER_ID", "0").strip() or "0")
        if not bot_token:
            raise RuntimeError("BOT_TOKEN is required")
        if not owner_id:
            raise RuntimeError("OWNER_ID is required")

        auth_users = _parse_int_set(os.environ.get("AUTH_USERS"))
        auth_users.add(owner_id)

        download_location = Path(
            os.environ.get("DOWNLOAD_LOCATION", "./DOWNLOADS").strip() or "./DOWNLOADS"
        )

        return cls(
            bot_token=bot_token,
            owner_id=owner_id,
            auth_users=auth_users,
            download_location=download_location,
            chunk_size=_parse_chunk_size(os.environ.get("CHUNK_SIZE")),
            http_proxy=os.environ.get("HTTP_PROXY", "").strip(),
            process_max_timeout=int(os.environ.get("PROCESS_MAX_TIMEOUT", "3700")),
        )

    @property
    def thumbnails_dir(self) -> Path:
        return self.download_location / "thumbnails"

    @property
    def requests_dir(self) -> Path:
        return self.download_location / "requests"

    @property
    def work_dir(self) -> Path:
        return self.download_location / "work"

    def ensure_directories(self) -> None:
        for path in (
            self.download_location,
            self.thumbnails_dir,
            self.requests_dir,
            self.work_dir,
        ):
            path.mkdir(parents=True, exist_ok=True)
