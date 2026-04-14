import logging
from urllib.parse import urlsplit, urlunsplit


def setup_logging() -> None:
    logging.basicConfig(
        force=True,
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
        datefmt="%H:%M:%S",
    )
    logging.getLogger("aiohttp").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)


def safe_url_label(url: str) -> str:
    parts = urlsplit(url)
    path = parts.path
    if len(path) > 60:
        path = f"{path[:57]}..."
    return urlunsplit((parts.scheme, parts.netloc, path, "", ""))


def redact_command(command: list[str]) -> list[str]:
    redacted: list[str] = []
    mask_next = False
    for item in command:
        if mask_next:
            redacted.append("***")
            mask_next = False
            continue
        if item in {"--password", "--username", "--proxy"}:
            redacted.append(item)
            mask_next = True
            continue
        if item.startswith("http://") or item.startswith("https://"):
            redacted.append(safe_url_label(item))
            continue
        redacted.append(item)
    return redacted
