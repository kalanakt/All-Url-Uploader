import os
import logging
import asyncio
from datetime import datetime
import re
from pyrogram.raw.all import layer
from pyrogram import Client, idle, __version__, filters
from pyrogram.errors import SessionPasswordNeeded
from config import Config
from aiohttp import web

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

if not os.path.isdir(Config.DOWNLOAD_LOCATION):
    os.makedirs(Config.DOWNLOAD_LOCATION)

if not Config.BOT_TOKEN or not Config.API_ID or not Config.API_HASH:
    logger.error("Please set BOT_TOKEN, API_ID and API_HASH in config.py or as env vars")
    quit(1)

start_time = datetime.utcnow()

task_queue = asyncio.Queue()
current_task = None

user_link_input_state = {}  # Tracks users waiting for queue URLs input
user_batch_state = {}  # Tracks users current batch state for /batch command

user_sessions = {}  # user_id -> string_session
user_clients = {}   # user_id -> Client instance (user client)


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
        return
    while not task_queue.empty():
        current_task = await task_queue.get()
        task_id, url, user_id = current_task
        try:
            logger.info(f"Starting task #{task_id}: {url}")
            await bot.send_message(user_id, f"Starting task #{task_id}: {url}")
            # TODO: Replace with your actual download/upload logic
            await asyncio.sleep(10)
            await bot.send_message(user_id, f"Finished task #{task_id}")
            logger.info(f"Finished task #{task_id}")
        except Exception as e:
            await bot.send_message(user_id, f"Error in task #{task_id}: {str(e)}")
            logger.error(f"Error in task #{task_id}: {str(e)}")
        current_task = None


async def process_batch_download(client: Client, user_id: int, chat_id: int, start_msg_id: int, count: int):
    pinned_msg = await client.send_message(user_id, f"📌 Batch download started: 0 / {count}")

    try:
        await pinned_msg.pin()
    except Exception as e:
        logger.warning(f"Could not pin message: {e}")

    completed = 0
    skipped = 0
    start_time_batch = datetime.utcnow()

    for offset in range(count):
        msg_id = start_msg_id + offset
        try:
            msg = await client.get_messages(chat_id, msg_id)
            if not msg or not msg.media:
                skipped += 1
                continue

            file_path = await client.download_media(msg)
            await client.send_document(user_id, file_path)
            os.remove(file_path)

            completed += 1
        except Exception as e:
            skipped += 1
            logger.error(f"Error processing message {msg_id}: {e}")

        elapsed = (datetime.utcnow() - start_time_batch).total_seconds()
        remain = count - (completed + skipped)
        eta = f"{int(remain * (elapsed / completed))} seconds" if completed > 0 else "Unknown"

        status_text = (
            f"📌 Batch download in progress:\n"
            f"✅ Completed: {completed}\n"
            f"⏭ Skipped: {skipped}\n"
            f"📥 Remaining: {remain}\n"
            f"⏳ ETA: {eta}"
        )
        try:
            await pinned_msg.edit(status_text)
        except Exception:
            pass

    try:
        await pinned_msg.unpin()
    except Exception:
        pass

    await client.send_message(
        user_id,
        f"✅ Batch download completed.\nTotal: {count}, Completed: {completed}, Skipped: {skipped}"
    )


async def main():
    bot = Client(
        "All-Url-Uploader",
        api_id=Config.API_ID,
        api_hash=Config.API_HASH,
        bot_token=Config.BOT_TOKEN,
        workers=50,
        plugins=dict(root="plugins"),
    )

    # LOGIN COMMAND
    @bot.on_message(filters.command("login") & filters.private)
    async def login_handler(client, message):
        user_id = message.from_user.id
        if user_id in user_clients:
            await message.reply_text("You are already logged in.")
            return

        await message.reply_text("Send your phone number with country code (e.g., +123456789):")

        try:
            phone_msg = await bot.listen(message.chat.id, filters=filters.private, timeout=120)
            phone_number = phone_msg.text.strip()

            temp_client = Client(f"user_{user_id}_temp")

            await temp_client.start(phone_number=phone_number)

            await message.reply_text("Send the login code you received on Telegram:")

            code_msg = await bot.listen(message.chat.id, timeout=120)
            code = code_msg.text.strip()

            try:
                await temp_client.sign_in(phone_number, code)

                if await temp_client.check_password():
                    await message.reply_text("Send your 2FA password:")
                    password_msg = await bot.listen(message.chat.id, timeout=120)
                    password = password_msg.text.strip()
                    await temp_client.check_password(password)

                string_session = temp_client.export_session_string()
                user_sessions[user_id] = string_session

                user_clients[user_id] = Client(f"user_session_{user_id}", session_string=string_session)
                await user_clients[user_id].start()

                await message.reply_text("✅ Login successful!")

            except SessionPasswordNeeded:
                await message.reply_text("2FA required but not provided. Login failed.")

            await temp_client.stop()

        except asyncio.TimeoutError:
            await message.reply_text("Login timed out. Please try again.")
        except Exception as e:
            await message.reply_text(f"An error occurred: {str(e)}")

    # LOGOUT COMMAND
    @bot.on_message(filters.command("logout") & filters.private)
    async def logout_handler(client, message):
        user_id = message.from_user.id
        if user_id not in user_clients:
            await message.reply_text("You are not logged in.")
            return
        await user_clients[user_id].stop()
        user_clients.pop(user_id, None)
        user_sessions.pop(user_id, None)
        await message.reply_text("👋 You have been logged out successfully.")

    # ACCESS WITH USER CLIENT EXAMPLE
    @bot.on_message(filters.command("mygroups") & filters.private)
    async def my_groups(client, message):
        user_id = message.from_user.id
        user_client = user_clients.get(user_id)
        if not user_client:
            await message.reply_text("You need to /login first to access private groups.")
            return
        dialogs = await user_client.get_dialogs()
        groups = [d.chat.title for d in dialogs if d.chat.type in ["group", "supergroup"]]
        if not groups:
            await message.reply_text("You have no accessible groups.")
            return
        await message.reply_text("Your groups:\n" + "\n".join(groups))

    # /batch command start and handler

    @bot.on_message(filters.command("batch") & filters.private)
    async def batch_start(client, message):
        user_batch_state[message.from_user.id] = {"step": "await_start_link"}
        await message.reply_text("🚀 Send me the starting Telegram message link from where you want to download.")

    @bot.on_message(filters.private)
    async def batch_handler(client, message):
        user_id = message.from_user.id
        state = user_batch_state.get(user_id)
        if not state:
            return

        if state["step"] == "await_start_link":
            text = message.text.strip()
            m = re.match(r"https://t.me/c/(\d+)/(\d+)", text)
            if not m:
                await message.reply_text(
                    "⚠️ Invalid link format. Please send a link like:\nhttps://t.me/c/2793359066/48"
                )
                return

            chat_id = int("-100" + m.group(1))
            start_msg_id = int(m.group(2))
            user_batch_state[user_id].update(
                {"chat_id": chat_id, "start_msg_id": start_msg_id, "step": "await_count"}
            )
            await message.reply_text("📥 How many files do you want to download? (max 10000)")
            return

        if state["step"] == "await_count":
            try:
                count = int(message.text.strip())
                if count < 1 or count > 10000:
                    raise ValueError()
            except ValueError:
                await message.reply_text("⚠️ Please send a valid number between 1 and 10000.")
                return

            user_batch_state[user_id]["count"] = count
            user_batch_state[user_id]["step"] = "downloading"

            await message.reply_text(f"⏳ Starting batch download of {count} files...")
            asyncio.create_task(
                process_batch_download(
                    client,
                    user_id,
                    user_batch_state[user_id]["chat_id"],
                    user_batch_state[user_id]["start_msg_id"],
                    user_batch_state[user_id]["count"],
                )
            )
            user_batch_state.pop(user_id, None)

    # /queue command
    @bot.on_message(filters.command("queue") & filters.private)
    async def queue_command_handler(client, message):
        user_link_input_state[message.from_user.id] = True
        await message.reply_text("📥 Send me one or more URLs separated by spaces or new lines.")

    # Collect links for /queue
    @bot.on_message(filters.private)
    async def collect_links_handler(client, message):
        user_id = message.from_user.id
        if user_link_input_state.get(user_id):
            text = message.text.strip()
            links = [link.strip() for link in text.split() if link.strip()]
            if not links:
                await message.reply_text("No valid links detected. Please send at least one link.")
                return

            count = len(links)
            user_link_input_state[user_id] = False

            for idx, url in enumerate(links, start=task_queue.qsize() + 1):
                await task_queue.put((idx, url, user_id))
            await message.reply_text(f"✅ Added {count} link(s) to the queue.")
            await process_next_task(bot)

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
        await message.reply_text(f"🤖 Bot is running.\n🕒 Uptime: {hours}h {minutes}m {seconds}s")

    @bot.on_message(filters.command("help") & filters.private)
    async def help_handler(client, message):
        help_text = (
            "🤖 **Bot Command List:**\n\n"
            "➕ /addtotask <url> - Add a new upload task\n"
            "📋 /queue - Add multiple URLs to queue (bot will ask for input)\n"
            "⏭ /skip - Skip the current running task\n"
            "🚀 /batch - Start batch sequential download from a Telegram link\n"
            "🔐 /login - Login to access private groups\n"
            "🔓 /logout - Logout of user session\n"
            "📂 /mygroups - List your accessible groups\n"
            "🏓 /ping - Check bot status and uptime\n"
            "❓ /help - Show this help message"
        )
        await message.reply_text(help_text)

    await bot.start()
    logger.info(f"**Bot Started**\n\n**Pyrogram Version:** {__version__}\n**Layer:** {layer}")
    logger.info("Developed by github.com/kalanakt Sponsored by www.netronk.com")

    await asyncio.gather(run_webserver(), idle())

    await bot.stop()
    logger.info("Bot Stopped ;)")

if __name__ == "__main__":
    asyncio.run(main())