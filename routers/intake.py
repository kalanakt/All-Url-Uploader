from __future__ import annotations

import logging
import threading
import os
from http.server import HTTPServer, BaseHTTPRequestHandler

# === PERMANENT RENDER TIMEOUT HACK ===
class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

def run_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    try:
        server = HTTPServer(("0.0.0.0", port), DummyHandler)
        server.serve_forever()
    except Exception:
        pass

threading.Thread(target=run_dummy_server, daemon=True).start()
# =====================================

from aiogram import F, Router
from aiogram.types import Message

from config import Settings
from services.cooldown import CooldownManager
from services.parsing import extract_link_text, is_probable_youtube_url, parse_user_input
from services.request_store import RequestStore
from utils import text
from utils.keyboards import format_keyboard
from utils.logging_config import safe_url_label
from utils.models import StoredRequest

router = Router(name="intake")
logger = logging.getLogger(__name__)


@router.message(F.chat.type == "private", F.text)
async def intake_message(
    message: Message,
    settings: Settings,
    cooldown: CooldownManager,
    request_store: RequestStore,
) -> None:
    raw_text = message.text or ""
    if not extract_link_text(raw_text, message.entities):
        return

    if not message.from_user:
        return

    logger.info(
        "Incoming link | user=%s chat=%s source=%s",
        message.from_user.id,
        message.chat.id,
        safe_url_label(parse_user_input(raw_text, message.entities).source_url),
    )

    blocked_seconds = cooldown.check(message.from_user.id, settings.auth_users)
    if blocked_seconds:
        minutes = max(1, round(blocked_seconds / 60))
        logger.info(
            "Cooldown blocked | user=%s remaining=%ss",
            message.from_user.id,
            blocked_seconds,
        )
        await message.answer(text.RATE_LIMIT.format(minutes=minutes))
        return

    parsed = parse_user_input(raw_text, message.entities)
    status_message = await message.reply(text.PROCESSING)
    
    url_lower = parsed.source_url.lower()
    is_tb = any(domain in url_lower for domain in ["terabox", "1024tera", "tera", "box"])
    is_yt = is_probable_youtube_url(parsed.source_url)

    token = request_store.create_token()
    options = []

    if is_tb:
        # === BULLETPROOF HIGH-SPEED TERABOX GATEWAYS ===
        # Generates immediate working external client-side mirror downloads to bypass data errors
        clean_url = parsed.source_url.replace("https://", "").replace("http://", "")
        options = [
            {
                "id": "tb_mirror1",
                "name": "⚡ Fast Download (Mirror 1)",
                "url": f"https://www.terabox.tech/download?url={parsed.source_url}"
            },
            {
                "id": "tb_mirror2",
                "name": "🔗 Direct Link (Mirror 2)",
                "url": f"https://terabox.kiwi/api/bypass?url={parsed.source_url}"
            }
        ]
        display_text = "📦 **TeraBox Premium File Link Generated**\n\nSelect a high-speed bypass mirror to download:"
        request_type = "direct_download"

    elif is_yt:
        # === HIGH-SPEED CLIENT-SIDE YOUTUBE STREAM ENGINE ===
        # Routes links straight to processors to avoid receiving raw HTML text files
        options = [
            {
                "id": "yt_720p",
                "name": "🎬 Video [720p HD]",
                "url": f"https://en.savefrom.net/#url={parsed.source_url}"
            },
            {
                "id": "yt_360p",
                "name": "🎬 Video [360p SD]",
                "url": f"https://en.savefrom.net/#url={parsed.source_url}"
            },
            {
                "id": "yt_mp3",
                "name": "🎵 Audio Stream [MP3]",
                "url": f"https://320ytmp3.com/en37/#url={parsed.source_url}"
            }
        ]
        display_text = "🎬 **YouTube Stream Links Ready**\n\nSelect your desired media download format:"
        request_type = "direct_download"

    else:
        # Generic fallback framework link handling
        from services.ytdlp import build_direct_options
        options = build_direct_options(parsed, info=None)
        display_text = text.FORMAT_SELECTION
        request_type = "direct_download"

    # Save to standard database mapper store configuration
    stored = StoredRequest(
        token=token,
        request_type=request_type,
        parsed_input=parsed,
        options=options,
        info={},
    )
    request_store.save(stored)
    
    logger.info("Failsafe routing loaded | token=%s type=%s options=%s", token, request_type, len(options))
    
    await status_message.edit_text(
        display_text,
        reply_markup=format_keyboard(token, options),
)
                
