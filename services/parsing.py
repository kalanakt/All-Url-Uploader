from __future__ import annotations

from urllib.parse import urlparse

from aiogram.types import MessageEntity

from utils.models import ParsedInput


def extract_link_text(text: str, entities: list[MessageEntity] | None) -> str | None:
    if entities:
        for entity in entities:
            if entity.type == "text_link" and entity.url:
                return entity.url
            if entity.type == "url":
                return text[entity.offset : entity.offset + entity.length]
    if "http://" in text or "https://" in text:
        return text
    return None


def _extract_url(text: str, entities: list[MessageEntity] | None) -> str:
    entity_url = extract_link_text(text, entities)
    if not entity_url:
        raise ValueError("No URL found in the message")
    return entity_url.strip()


def parse_user_input(
    text: str, entities: list[MessageEntity] | None = None
) -> ParsedInput:
    if "|" in text:
        parts = [part.strip() for part in text.split("|")]
        if len(parts) == 2:
            return ParsedInput(source_url=parts[0], custom_file_name=parts[1])
        if len(parts) == 4:
            return ParsedInput(
                source_url=parts[0],
                custom_file_name=parts[1],
                username=parts[2],
                password=parts[3],
            )

    if " * " in text:
        url, file_name = [part.strip() for part in text.split(" * ", maxsplit=1)]
        return ParsedInput(source_url=url, custom_file_name=file_name)

    return ParsedInput(source_url=_extract_url(text, entities))


def is_probable_youtube_url(url: str) -> bool:
    hostname = urlparse(url).netloc.lower()
    return "youtube.com" in hostname or "youtu.be" in hostname
