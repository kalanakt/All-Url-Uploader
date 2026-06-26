from aiogram import F, Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from services.parsing import extract_link_text, is_probable_youtube_url, parse_user_input
from config import Settings
from services.cooldown import CooldownManager

router = Router(name="intake")

@router.message(F.chat.type == "private", F.text)
async def intake_message(message: Message, settings: Settings, cooldown: CooldownManager) -> None:
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
        
    elif is_yt:
        display_text = "🎬 **YouTube Link Detected:**\nChoose your preferred format to download directly:"
        # These callbacks send the instructions straight to your callbacks_router
        buttons = [
            [
                InlineKeyboardButton(text="📺 720p Video", callback_data=f"dl_video_720p|{url}"),
                InlineKeyboardButton(text="📺 480p Video", callback_data=f"dl_video_480p|{url}")
            ],
            [
                InlineKeyboardButton(text="🎵 MP3 Audio", callback_data=f"dl_audio_mp3|{url}")
            ]
        ]
        
    else:
        await message.reply("Link recognized but no direct handler available.")
        return

    await message.reply(display_text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
        
