import os
import logging
import asyncio
from pyrogram.raw.all import layer
from pyrogram import Client, idle, __version__
from config import Config
from aiohttp import web

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

# Ensure download directory exists
os.makedirs(Config.DOWNLOAD_LOCATION, exist_ok=True)

# Validate env vars
for var, name in [
    (Config.BOT_TOKEN, "BOT_TOKEN"),
    (Config.API_ID, "API_ID"),
    (Config.API_HASH, "API_HASH")
]:
    if not var:
        logger.error(f"Please set {name} in config.py or as env var")
        quit(1)

# --- Web Server ---
async def handle(request):
    return web.Response(text="Bot is running ✅")

async def run_webserver():
    app = web.Application()
    app.router.add_get('/', handle)
    port = int(os.environ.get("PORT", 8080))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logger.info(f"🌐 Web server running on port {port}")

# --- Main Bot ---
async def main():
    bot = Client(
        "All-Url-Uploader",
        api_id=Config.API_ID,
        api_hash=Config.API_HASH,
        bot_token=Config.BOT_TOKEN,
        workers=50,
        plugins=dict(root="plugins"),
    )

    await bot.start()
    logger.info("🤖 Bot started successfully!")
    logger.info(f"Pyrogram v{__version__} | Layer {layer}")

    # Run webserver in the background
    asyncio.create_task(run_webserver())

    await idle()
    await bot.stop()
    logger.info("Bot stopped gracefully.")

if __name__ == "__main__":
    asyncio.run(main())