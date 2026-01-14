import os
import logging
import asyncio
import time
from pyrogram.raw.all import layer
from pyrogram import Client, idle, __version__, filters
from config import Config
from aiohttp import web

# ---------------- LOGGING ----------------
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

# ---------------- CHECK FOLDERS ----------------
if not os.path.isdir(Config.DOWNLOAD_LOCATION):
    os.makedirs(Config.DOWNLOAD_LOCATION)

if not Config.BOT_TOKEN or not Config.API_ID or not Config.API_HASH:
    logger.error("Missing required config values!")
    quit(1)

# ---------------- TASK QUEUE ----------------
task_queue = asyncio.Queue()
current_task = None
bot_start_time = time.time()  # For /ping uptime

# ---------------- WEB SERVER ----------------
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


# ---------------- TASK PROCESSOR ----------------
async def process_next_task(bot: Client):
    global current_task

    if current_task is not None:
        return  # already running a task

    while not task_queue.empty():
        current_task = await task_queue.get()
        task_id, url, user_id = current_task

        try:
            logger.info(f"Starting task #{task_id}: {url}")
            await bot.send_message(user_id, f"🚀 Starting task **#{task_id}**\nURL: `{url}`")

            # Simulate processing
            await asyncio.sleep(10)

            await bot.send_message(user_id, f"✅ Finished task #{task_id}")
            logger.info(f"Finished task #{task_id}")

        except Exception as e:
            await bot.send_message(user_id, f"❌ Error in task #{task_id}: {str(e)}")
            logger.error(f"Error in task #{task_id}: {str(e)}")

        current_task = None


# ---------------- MAIN BOT ----------------
async def main():

    bot = Client(
        "All-Url-Uploader",
        api_id=Config.API_ID,
        api_hash=Config.API_HASH,
        bot_token=Config.BOT_TOKEN,
        workers=50,
        plugins=dict(root="plugins"),
    )

    # ------ /start ------
    @bot.on_message(filters.command("start") & filters.private)
    async def start_handler(client, message):
        text = (
            "👋 **Welcome to All URL Uploader Bot!**\n\n"
            "Available commands:\n"
            "➕ /addtotask `<url>` – Add a new URL task\n"
            "📋 /queue – Show pending tasks\n"
            "⏭️ /skip – Skip current running task\n"
            "🏓 /ping – Check bot uptime\n"
            "📊 /status – Show current running task\n"
        )
        await message.reply_text(text)

    # ------ /ping ------
    @bot.on_message(filters.command("ping") & filters.private)
    async def ping_handler(client, message):
        uptime = time.time() - bot_start_time
        hours = int(uptime // 3600)
        minutes = int((uptime % 3600) // 60)
        seconds = int(uptime % 60)

        await message.reply_text(
            f"🏓 **Pong!**\n"
            f"⏱ **Uptime:** {hours}h {minutes}m {seconds}s\n"
            f"⚙ Pyrogram: {__version__}\n"
            f"📡 Layer: {layer}"
        )

    # ------ /status ------
    @bot.on_message(filters.command("status") & filters.private)
    async def status_handler(client, message):
        global current_task

        if current_task:
            txt = (
                f"🔄 **Currently Running Task:**\n"
                f"#{current_task[0]} - {current_task[1]}\n\n"
            )
        else:
            txt = "🟢 No task running currently.\n\n"

        txt += f"📌 Pending in queue: {task_queue.qsize()}"
        await message.reply_text(txt)

    # ------ /addtotask ------
    @bot.on_message(filters.command("addtotask") & filters.private)
    async def addtotask_handler(client, message):
        if len(message.command) < 2:
            return await message.reply_text("Usage: `/addtotask <url>`")

        url = message.command[1]
        task_id = task_queue.qsize() + 1
        user_id = message.from_user.id

        await task_queue.put((task_id, url, user_id))
        await message.reply_text(f"🆗 Added task **#{task_id}** to queue.")

        await process_next_task(bot)

    # ------ /queue ------
    @bot.on_message(filters.command("queue") & filters.private)
    async def queue_handler(client, message):
        if task_queue.empty():
            return await message.reply_text("📭 Queue is empty.")

        tasks = list(task_queue._queue)
        txt = "📋 **Task Queue:**\n" + "\n".join(f"#{t[0]} → {t[1]}" for t in tasks)

        await message.reply_text(txt)

    # ------ /skip ------
    @bot.on_message(filters.command("skip") & filters.private)
    async def skip_handler(client, message):
        global current_task

        if current_task is None:
            return await message.reply_text("⚠ No task is running right now.")

        await message.reply_text(f"⏭️ Skipping task **#{current_task[0]}**")
        current_task = None

        await process_next_task(bot)

    # ------ START BOT ------
    await bot.start()
    logger.info(f"Bot Started | Pyrogram {__version__} | Layer {layer}")

    await asyncio.gather(
        run_webserver(),
        idle()
    )

    await bot.stop()
    logger.info("Bot stopped.")


if __name__ == "__main__":
    asyncio.run(main())