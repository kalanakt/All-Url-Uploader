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
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from config import Settings
from services.cooldown import CooldownManager
from services.parsing import extract_link_text, is_probable_youtube_url, parse_user_input
from utils import text
from utils.logging_config import safe_url_label

router = Router(name="intake")
logger = logging.getLogger(__name__)

@router.message(F.chat.type == "private", F.text)
async def intake_message(
    message: Message,
    settings: Settings,
    cooldown: CooldownManager,
) -> None:
    raw_text = message.text or ""
    if not extract_link_text(raw_text, message.entities):
        return

    parsed = parse_user_input(raw_text, message.entities)
    url_lower = parsed.source_url.lower()
    is_tb = any(domain in url_lower for domain in ["terabox", "1024tera", "tera", "box"])
    is_yt = is_probable_youtube_url(parsed.source_url)

    # DIRECT FIRE BUTTON GENERATOR (NO DATABASE REQUIRED)
    buttons = []
    if is_tb:
        display_text = "📦 **TeraBox Mirror Links:**"
        buttons = [
            [InlineKeyboardButton(text="⚡ Mirror 1", url=f"https://www.terabox.tech/download?url={parsed.source_url}")],
            [InlineKeyboardButton(text="🔗 Mirror 2", url=f"https://terabox.kiwi/api/bypass?url={parsed.source_url}")]
        ]
    elif is_yt:
        display_text = "🎬 **YouTube Stream Links:**"
        buttons = [
            [InlineKeyboardButton(text="🎬 720p HD", url=f"https://en.savefrom.net/#url={parsed.source_url}")],
            [InlineKeyboardButton(text="🎬 360p SD", url=f"https://en.savefrom.net/#url={parsed.source_url}")],
            [InlineKeyboardButton(text="🎵 Audio MP3", url=f"https://320ytmp3.com/en37/#url={parsed.source_url}")]
        ]
    else:
        await message.reply("Link detected, but format not recognized.")
        return

    # Delete the "Processing" message and send new ones immediately
    await message.reply(display_text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    logger.info("Direct buttons fired for %s", safe_url_label(parsed.source_url))
        
