import uuid
import logging
from aiogram import F, Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from services.parsing import extract_link_text, is_probable_youtube_url, parse_user_input
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
    raw_text = message.text or ""
    
    # Retrieve the state storage context
    request_store = kwargs.get("request_store")
    if not request_store:
        logger.error("DEBUG: request_store object was NOT found in kwargs context!")
        return

    # Extract and clean up link text layout
    if not extract_link_text(raw_text, message.entities):
        return

    try:
        parsed = parse_user_input(raw_text, message.entities)
        url = parsed.source_url
    except Exception as e:
        logger.exception("DEBUG: parse_user_input crashed: %s", e)
        return
    
    url_lower = url.lower()
    is_tb = any(domain in url_lower for domain in ["terabox", "1024tera", "tera", "box"])
    
    # BROAD MATCH FIX: Match standard or short-code formats seamlessly
    is_yt = is_probable_youtube_url(url) or "youtube.com" in url_lower or "youtu.be" in url_lower

    if is_tb:
        display_text = "📦 **TeraBox Link Detected:**"
        buttons = [[InlineKeyboardButton(text="📥 Download TeraBox File", url=f"https://terabox.com/sharing/link?surl={url.split('/')[-1]}")]]
        await message.reply(display_text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
        return
        
    elif is_yt:
        display_text = "🎬 **YouTube Link Detected:**\nChoose your preferred format to download directly:"
        token = uuid.uuid4().hex[:8]
        
        options = [
            DownloadOption(option_id="720p", label="📺 720p Video", send_type="video", format_id="bestvideo[height<=720]+bestaudio/best[height<=720]"),
            DownloadOption(option_id="480p", label="📺 480p Video", send_type="video", format_id="bestvideo[height<=480]+bestaudio/best[height<=480]"),
            DownloadOption(option_id="mp3", label="🎵 MP3 Audio", send_type="audio", format_id="bestaudio/best")
        ]
        
        stored_request = StoredRequest(
            token=token,
            request_type="youtube_quick",
            parsed_input=parsed,
            options=options,
            info={}
        )
        request_store.save(stored_request)
        
        inline_keyboard = [
            [
                InlineKeyboardButton(text="📺 720p Video", callback_data=RequestCallback(token=token, action="720p").pack()),
                InlineKeyboardButton(text="📺 480p Video", callback_data=RequestCallback(token=token, action="480p").pack())
            ],
            [
                InlineKeyboardButton(text="🎵 MP3 Audio", callback_data=RequestCallback(token=token, action="mp3").pack())
            ]
        ]
        
        await message.reply(display_text, reply_markup=InlineKeyboardMarkup(inline_keyboard=inline_keyboard))
        
    else:
        await message.reply("Link recognized but no direct handler available.")
        
