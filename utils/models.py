from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class ParsedInput:
    source_url: str
    custom_file_name: str | None = None
    username: str | None = None
    password: str | None = None


@dataclass(slots=True)
class DownloadOption:
    option_id: str
    label: str
    send_type: str
    mode: str
    format_id: str | None = None
    file_ext: str | None = None
    audio_quality: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "DownloadOption":
        return cls(**payload)


@dataclass(slots=True)
class StoredRequest:
    token: str
    request_type: str
    parsed_input: ParsedInput
    options: list[DownloadOption] = field(default_factory=list)
    info: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "token": self.token,
            "request_type": self.request_type,
            "parsed_input": asdict(self.parsed_input),
            "options": [option.to_dict() for option in self.options],
            "info": self.info,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "StoredRequest":
        return cls(
            token=payload["token"],
            request_type=payload["request_type"],
            parsed_input=ParsedInput(**payload["parsed_input"]),
            options=[DownloadOption.from_dict(item) for item in payload["options"]],
            info=payload.get("info", {}),
        )


@dataclass(slots=True)
class DownloadArtifact:
    path: Path
    file_name: str
    send_type: str
    caption: str
