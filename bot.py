import os
import logging
import asyncio
from datetime import datetime
from pyrogram.raw.all import layer
from pyrogram import Client, idle, __version__, filters
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

# Bot start time to calculate uptime
start_time = datetime.utcnow()

# Queue to hold tasks: (task_id, url, user_id)
task_queue = asyncio.Queue()

# Current running task info
current_task = None


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


async def process_next_task(bot: Client):
    global current_task
    if current_task is not None:
        return  # Task is already running

    while not task_queue.empty():
        current_task = await task_queue.get()
        task_id, url, user_id = current_task
        try:
            logger.info(f"Starting task #{task_id}: {url}")
            await bot.send_message(user_id, f"Starting task #{task_id}: {url}")
            # Simulate task processing: replace with your actual download/upload logic
            await asyncio.sleep(10)
            await bot.send_message(user_id, f"Finished task #{task_id}")
            logger.info(f"Finished task #{task_id}")
        except Exception as e:
            await bot.send_message(user_id, f"Error in task #{task_id}: {str(e)}")
            logger.error(f"Error in task #{task_id}: {str(e)}")
        current_task = None


async def main():
    bot = Client(
        "All-Url-Uploader",
        api_id=Config.API_ID,
        api_hash=Config.API_HASH,
        bot_token=Config.BOT_TOKEN,
        workers=50,
        plugins=dict(root="plugins"),
    )

    @bot.on_message(filters.command("addtotask") & filters.private)
    async def addtotask_handler(client, message):
        if len(message.command) < 2:
            await message.reply_text("Usage: /addtotask <url>")
            return
        url = message.command[1]
        task_id = task_queue.qsize() + 1
        user_id = message.from_user.id
        await task_queue.put((task_id, url, user_id))
        await message.reply_text(f"Task #{task_id} added to queue.")
        await process_next_task(bot)

    @bot.on_message(filters.command("queue") & filters.private)
    async def show_queue_handler(client, message):
        if task_queue.empty():
            await message.reply_text("The task queue is empty.")
            return
        tasks = list(task_queue._queue)
        text = "📋 Current task queue:
" + "
".join(f"#{t[0]}: {t[1]}" for t in tasks)
        await message.reply_text(text)

    @bot.on_message(filters.command("skip") & filters.private)
    async def skip_task_handler(client, message):
        global current_task
        if current_task is None:
            await message.reply_text("No task is currently running.")
            return
        await message.reply_text(f"⏭ Skipping task #{current_task[0]}")
        current_task = None
        await process_next_task(bot)

    @bot.on_message(filters.command("ping") & filters.private)
    async def ping_handler(client, message):
        uptime = datetime.utcnow() - start_time
        hours, remainder = divmod(int(uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        await message.reply_text(f"🤖 Bot is running.
🕒 Uptime: {hours}h {minutes}m {seconds}s")

    @bot.on_message(filters.command("help") & filters.private)
    async def help_handler(client, message):
        help_text = (
            "🤖 **Bot Command List:**

"
            "➕ /addtotask `<url>` - Add a new upload task
"
            "📋 /queue - Show tasks in queue
"
            "⏭ /skip - Skip the current running task
"
            "🏓 /ping - Check bot status and uptime
"
            "❓ /help - Show this help message
"
        )
        await message.reply_text(help_text)

    await bot.start()
    logger.info("Bot has started.")
    logger.info("**Bot Started**

**Pyrogram Version:** %s 
**Layer:** %s", __version__, layer)
    logger.info("Developed by github.com/kalanakt Sponsored by www.netronk.com")

    # Run webserver and keep bot idle concurrently
    await asyncio.gather(run_webserver(), idle())

    await bot.stop()
    logger.info("Bot Stopped ;)")


if __name__ == "__main__":
    asyncio.run(main())