import uuid
from aiogram import F, Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from services.parsing import extract_link_text, is_probable_youtube_url, parse_user_input
from config import Settings
from services.cooldown import CooldownManager
from services.request_store import RequestStore
from utils.callbacks import RequestCallback
from utils.models import StoredRequest, DownloadOption

router = Router(name="intake")

@router.message(F.chat.type == "private", F.text)
async def intake_message(
    message: Message, 
    settings: Settings, 
    cooldown: CooldownManager,
    request_store: RequestStore
) -> None:
    raw_text = message.text or ""
    if not extract_link_text(raw_text, message.entities):
        return

    parsed = parse_user_input(raw_text, message.entities)
    url = parsed.source_url
    
    is_tb = any(domain in url.lower() for domain in ["terabox", "1024tera", "tera", "box"])
    is_yt = is_probable_youtube_url(url)

    if is_tb:
        display_text = "📦 **TeraBox Link Detected:**"
        buttons = [[InlineKeyboardButton(text="📥 Download TeraBox File", url=f"https://terabox.com/sharing/link?surl={url.split('/')[-1]}")]]
        await message.reply(display_text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
        return
        
    elif is_yt:
        display_text = "🎬 **YouTube Link Detected:**\nChoose your preferred format to download directly:"
        
        # Generate a distinct internal registration token for this link sequence
        token = uuid.uuid4().hex[:8]
        
        # Structure the target extraction schemas expected by services/ytdlp.py
        options = [
            DownloadOption(option_id="720p", label="📺 720p Video", send_type="video", format_id="bestvideo[height<=720]+bestaudio/best[height<=720]"),
            DownloadOption(option_id="480p", label="📺 480p Video", send_type="video", format_id="bestvideo[height<=480]+bestaudio/best[height<=480]"),
            DownloadOption(option_id="mp3", label="🎵 MP3 Audio", send_type="audio", format_id="bestaudio/best")
        ]
        
        # Register the current request details securely inside the store
        stored_request = StoredRequest(
            token=token,
            request_type="youtube_quick",
            parsed_input=parsed,
            options=options,
            info={}
        )
        request_store.save(stored_request)
        
        # Package structural matching payloads using the exact internal callback schemas
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
        
