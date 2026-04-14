from __future__ import annotations

from pathlib import Path


class ThumbnailStore:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def path_for_user(self, user_id: int) -> Path:
        return self.root / f"{user_id}.jpg"

    def get(self, user_id: int) -> str | None:
        path = self.path_for_user(user_id)
        return str(path) if path.exists() else None

    def delete(self, user_id: int) -> bool:
        path = self.path_for_user(user_id)
        if not path.exists():
            return False
        path.unlink()
        return True
