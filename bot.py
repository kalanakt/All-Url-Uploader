import os
import logging
import asyncio
from pyrogram.raw.all import layer
from pyrogram import Client, idle, __version__
from config import Config
from aiohttp import web

# ---------------- Logging ----------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

# ---------------- Config Checks ----------------
if not os.path.isdir(Config.DOWNLOAD_LOCATION):
    os.makedirs(Config.DOWNLOAD_LOCATION)

for var, name in [
    (Config.BOT_TOKEN, "BOT_TOKEN"),
    (Config.API_ID, "API_ID"),
    (Config.API_HASH, "API_HASH")
]:
    if not var:
        logger.error(f"Please set {name} in config.py or as env var")
        quit(1)

# ---------------- Web Server ----------------
async def handle(request):
    return web.Response(text="✅ Bot is running!")

async def run_webserver():
    app = web.Application()
    app.router.add_get('/', handle)
    port = int(os.environ.get("PORT", 8080))  # Default 8080
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logger.info(f"🌐 HTTP server running on port {port}")

# ---------------- Main Logic ----------------
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
    logger.info("**Bot Started**\n\n**Pyrogram Version:** %s \n**Layer:** %s", __version__, layer)
    logger.info("Developed by github.com/kalanakt | Sponsored by www.netronk.com")

    # Run HTTP server in the background (non-blocking)
    asyncio.create_task(run_webserver())

    # Keep the bot running
    await idle()

    # Stop bot on exit
    await bot.stop()
    logger.info("Bot stopped gracefully. 👋")

# ---------------- Entry Point ----------------
if __name__ == "__main__":
    asyncio.run(main())