from __future__ import annotations

import json
import shutil
import uuid
from pathlib import Path

from utils.models import StoredRequest


class RequestStore:
    def __init__(self, requests_dir: Path, work_root: Path) -> None:
        self.requests_dir = requests_dir.resolve()
        self.work_root = work_root.resolve()
        self.requests_dir.mkdir(parents=True, exist_ok=True)
        self.work_root.mkdir(parents=True, exist_ok=True)

    def create_token(self) -> str:
        return uuid.uuid4().hex[:10]

    def _request_path(self, token: str) -> Path:
        return self.requests_dir / f"{token}.json"

    def work_directory(self, token: str) -> Path:
        path = self.work_root / token
        path.mkdir(parents=True, exist_ok=True)
        return path

    def save(self, stored_request: StoredRequest) -> None:
        self._request_path(stored_request.token).write_text(
            json.dumps(stored_request.to_dict()),
            encoding="utf-8",
        )

    def load(self, token: str) -> StoredRequest | None:
        path = self._request_path(token)
        if not path.exists():
            return None
        return StoredRequest.from_dict(json.loads(path.read_text(encoding="utf-8")))

    def delete(self, token: str) -> None:
        path = self._request_path(token)
        if path.exists():
            path.unlink()
        work_dir = self.work_root / token
        if work_dir.exists():
            shutil.rmtree(work_dir, ignore_errors=True)
