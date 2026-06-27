import uuid
import logging
from aiogram import F, Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from services.parsing import is_probable_youtube_url, parse_user_input
from config import Settings
from services.cooldown import CooldownManager
from utils.callbacks import RequestCallback
from utils.models import StoredRequest, DownloadOption

router = Router(name="intake")
logger = logging.getLogger(__name__)

@router.message(F.chat.type == "private", F.text)
async def intake_message(
    message: Message, 
    settings: Settings, 
    cooldown: CooldownManager,
    **kwargs
) -> None:
    try:
        raw_text = message.text or ""
        raw_text_lower = raw_text.lower()
        
        request_store = kwargs.get("request_store")
        if not request_store:
            await message.reply("❌ Error: Internal storage layer context is missing.")
            return

        is_link = any(marker in raw_text_lower for marker in ["http://", "https://", "www.", ".com", ".be", "tera"])
        if not is_link:
            return

        try:
            parsed = parse_user_input(raw_text, message.entities)
            url = parsed.source_url
        except Exception as parse_err:
            if "http" in raw_text:
                url = raw_text.strip()
                from unittest.mock import Mock
                parsed = Mock()
                
