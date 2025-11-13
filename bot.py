import os
import logging
import asyncio
from datetime import datetime
import re
from pyrogram.raw.all import layer
from pyrogram import Client, idle, __version__, filters
from pyrogram.errors import SessionPasswordNeeded, PhoneCodeInvalid, PhoneCodeExpired
from config import Config
from aiohttp import web

# ---------------- LOGGING ----------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

# ---------------- FOLDER SETUP ----------------
if not os.path.isdir(Config.DOWNLOAD_LOCATION):
    os.makedirs(Config.DOWNLOAD_LOCATION)
if not os.path.isdir("sessions"):
    os.makedirs("sessions")

# ---------------- CHECK CONFIG ----------------
if not Config.BOT_TOKEN or not Config.API_ID or not Config.API_HASH:
    logger.error("Please set BOT_TOKEN, API_ID and API_HASH in config.py or as env vars")
    quit(1)

# ---------------- GLOBAL VARIABLES ----------------
start_time = datetime.utcnow()
task_queue = asyncio.Queue()
current_task = None
user_link_input_state = {}
user_batch_state = {}
login_state = {}
user_clients = {}

# ---------------- WEB SERVER ----------------
async def handle(request):
    return web.Response(text="✅ Bot is running on Render")

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
        return
    while not task_queue.empty():
        current_task = await task_queue.get()
        task_id, url, user_id = current_task
        try:
            logger.info(f"Starting task #{task_id}: {url}")
            await bot.send_message(user_id, f"Starting task #{task_id}: {url}")
            # Simulated download
            await asyncio.sleep(10)
            await bot.send_message(user_id, f"✅ Finished task #{task_id}")
            logger.info(f"Finished task #{task_id}")
        except Exception as e:
            await bot.send_message(user_id, f"❌ Error in task #{task_id}: {str(e)}")
            logger.error(f"Error in task #{task_id}: {str(e)}")
        current_task = None

# ---------------- BATCH DOWNLOAD ----------------
async def process_batch_download(client: Client, user_id: int, chat_id: int, start_msg_id: int, count: int):
    pinned_msg = await client.send_message(user_id, f"📌 Batch download started: 0 / {count}")

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
        eta = f"{int(remain * (elapsed / completed))} sec" if completed > 0 else "Unknown"

        try:
            await pinned_msg.edit(
                f"📌 Progress:\n✅ {completed} done\n⏭ {skipped} skipped\n📥 {remain} left\n⏳ ETA: {eta}"
            )
        except Exception:
            pass

    await client.send_message(
        user_id, f"✅ Batch completed.\nTotal: {count}, Done: {completed}, Skipped: {skipped}"
    )

# ---------------- MAIN BOT ----------------
bot = Client(
    "All-Url-Uploader",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN,
    workers=50,
    plugins=dict(root="plugins"),
)

# ---------------- START ----------------
@bot.on_message(filters.command("start") & filters.private)
async def start_handler(client, message):
    await message.reply_text(
        "👋 **Hello!** I am your File Uploader Bot.\n\n"
        "Use /help to see available commands."
    )

# ---------------- LOGIN SYSTEM ----------------
@bot.on_message(filters.command("login") & filters.private)
async def login_start(client, message):
    user_id = message.from_user.id
    await message.reply_text("📱 Send your phone number with country code (e.g. +919876543210):")
    login_state[user_id] = {"step": "phone"}

@bot.on_message(filters.private)
async def login_process(client, message):
    user_id = message.from_user.id
    state = login_state.get(user_id)
    if not state:
        return

    # Step 1: Phone
    if state["step"] == "phone":
        phone = message.text.strip()
        await message.reply_text("📩 Sending login code...")
        user_client = Client(f"sessions/{user_id}", api_id=Config.API_ID, api_hash=Config.API_HASH)
        await user_client.connect()
        try:
            await user_client.send_code(phone)
            state.update({"client": user_client, "phone": phone, "step": "code"})
            await message.reply_text("✅ Code sent! Please send the code you received (e.g. 12345).")
        except Exception as e:
            await message.reply_text(f"❌ Error sending code: {e}")
        return

    # Step 2: Code
    if state["step"] == "code":
        code = message.text.strip()
        user_client = state["client"]
        phone = state["phone"]
        try:
            await user_client.sign_in(phone, code)
            user_clients[user_id] = user_client
            await message.reply_text("✅ Login successful! You can now access private groups.")
            del login_state[user_id]
        except SessionPasswordNeeded:
            state["step"] = "password"
            await message.reply_text("🔐 Two-step verification is enabled. Send your password:")
        except PhoneCodeInvalid:
            await message.reply_text("❌ Invalid code. Try again.")
        except PhoneCodeExpired:
            await message.reply_text("⚠️ Code expired. Please use /login again.")
        return

    # Step 3: Password
    if state["step"] == "password":
        password = message.text.strip()
        user_client = state["client"]
        try:
            await user_client.check_password(password)
            user_clients[user_id] = user_client
            await message.reply_text("✅ Login successful (2FA verified).")
            del login_state[user_id]
        except Exception as e:
            await message.reply_text(f"❌ Password error: {e}")
        return

# ---------------- LOGOUT ----------------
@bot.on_message(filters.command("logout") & filters.private)
async def logout(client, message):
    user_id = message.from_user.id
    if user_id in user_clients:
        try:
            await user_clients[user_id].log_out()
        except Exception:
            pass
        del user_clients[user_id]
        await message.reply_text("🔓 Logged out successfully.")
    else:
        await message.reply_text("⚠️ You are not logged in.")

# ---------------- MY GROUPS ----------------
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
        await message.reply_text("You have no groups.")
        return
    await message.reply_text("📂 Your groups:\n" + "\n".join(groups))

# ---------------- BATCH COMMAND ----------------
@bot.on_message(filters.command("batch") & filters.private)
async def batch_start(client, message):
    user_batch_state[message.from_user.id] = {"step": "await_start_link"}
    await message.reply_text("🚀 Send the starting Telegram message link (e.g. https://t.me/c/1234567/10)")

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
            await message.reply_text("⚠️ Invalid link format.")
            return
        chat_id = int("-100" + m.group(1))
        start_msg_id = int(m.group(2))
        state.update({"chat_id": chat_id, "start_msg_id": start_msg_id, "step": "await_count"})
        await message.reply_text("📥 How many files do you want to download? (max 10000)")
        return

    if state["step"] == "await_count":
        try:
            count = int(message.text.strip())
            if count < 1 or count > 10000:
                raise ValueError()
        except ValueError:
            await message.reply_text("⚠️ Invalid number. Try again.")
            return
        await message.reply_text(f"⏳ Starting batch download of {count} files...")
        asyncio.create_task(
            process_batch_download(
                client, user_id, state["chat_id"], state["start_msg_id"], count
            )
        )
        user_batch_state.pop(user_id, None)

# ---------------- OTHER COMMANDS ----------------
@bot.on_message(filters.command("addtotask") & filters.private)
async def addtotask_handler(client, message):
    if len(message.command) < 2:
        await message.reply_text("Usage: /addtotask <url>")
        return
    url = message.command[1]
    task_id = task_queue.qsize() + 1
    user_id = message.from_user.id
    await task_queue.put((task_id, url, user_id))
    await message.reply_text(f"✅ Task #{task_id} added.")
    await process_next_task(bot)

@bot.on_message(filters.command("skip") & filters.private)
async def skip_task_handler(client, message):
    global current_task
    if current_task is None:
        await message.reply_text("No running task.")
        return
    await message.reply_text(f"⏭ Skipping task #{current_task[0]}")
    current_task = None
    await process_next_task(bot)

@bot.on_message(filters.command("ping") & filters.private)
async def ping_handler(client, message):
    uptime = datetime.utcnow() - start_time
    h, r = divmod(int(uptime.total_seconds()), 3600)
    m, s = divmod(r, 60)
    await message.reply_text(f"🏓 Bot alive!\n🕒 Uptime: {h}h {m}m {s}s")

@bot.on_message(filters.command("help") & filters.private)
async def help_handler(client, message):
    help_text = (
        "🤖 **Bot Commands:**\n\n"
        "➕ /addtotask <url> - Add new task\n"
        "📋 /queue - Add multiple URLs\n"
        "⏭ /skip - Skip current task\n"
        "🚀 /batch - Start batch download\n"
        "🔐 /login - Login to access private groups\n"
        "🔓 /logout - Logout user session\n"
        "📂 /mygroups - Show your groups\n"
        "🏓 /ping - Check bot status\n"
        "❓ /help - Show this message"
    )
    await message.reply_text(help_text)

# ---------------- MAIN ----------------
async def main():
    await bot.start()
    logger.info(f"✅ Bot Started | Pyrogram v{__version__} | Layer {layer}")
    await asyncio.gather(run_webserver(), idle())
    await bot.stop()
    logger.info("🛑 Bot stopped")

if __name__ == "__main__":
    asyncio.run(main())