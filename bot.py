import os
import logging
import asyncio
from pyrogram.raw.all import layer
from pyrogram import Client, idle, __version__
from config import Config
from aiohttp import web

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

if not os.path.isdir(Config.DOWNLOAD_LOCATION):
    os.makedirs(Config.DOWNLOAD_LOCATION)

if not Config.BOT_TOKEN:
    logger.error("Please set BOT_TOKEN in config.py or as env var")
    quit(1)

if not Config.API_ID:
    logger.error("Please set API_ID in config.py or as env var")
    quit(1)

if not Config.API_HASH:
    logger.error("Please set API_HASH in config.py or as env var")
    quit(1)

async def handle(request):
    return web.Response(text="Bot is running")

async def run_webserver():
    app = web.Application()
    app.router.add_get('/', handle)
    port = int(os.environ.get("PORT", 8000))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logger.info(f"HTTP server running on port {port}")

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
    logger.info("Bot has started.")
    logger.info("**Bot Started**\n\n**Pyrogram Version:** %s \n**Layer:** %s", __version__, layer)
    logger.info("Developed by github.com/kalanakt Sponsored by www.netronk.com")

    # Run HTTP server and bot idle concurrently
    await run_webserver()
    await idle()

    await bot.stop()
    logger.info("Bot Stopped ;)")

if __name__ == "__main__":
    asyncio.run(main())
