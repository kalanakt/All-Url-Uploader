from pyrogram import Client, filters
from pyrogram.types import Message
import asyncio

# A simple FIFO queue to hold tasks (urls)
task_queue = asyncio.Queue()

# Current running task flag
current_task = None

async def process_next_task(bot: Client):
    global current_task
    if current_task is not None:
        return  # Task already running
    while not task_queue.empty():
        current_task = await task_queue.get()
        task_id, url, user_id = current_task
        try:
            # Notify user task started
            await bot.send_message(user_id, f"Starting task #{task_id}: {url}")
            # Simulate processing (replace with your actual task)
            await asyncio.sleep(10)  # Example delay for task processing

            # Notify user task finished
            await bot.send_message(user_id, f"Finished task #{task_id}")
        except Exception as e:
            await bot.send_message(user_id, f"Error while processing task #{task_id}: {str(e)}")
        current_task = None


@Client.on_message(filters.command("ping") & filters.private)
async def ping(bot: Client, message: Message):
    await message.reply_text("Pong!")


@Client.on_message(filters.command("addtotask") & filters.private)
async def addtotask(bot: Client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("Usage: /addtotask <url>")
        return
    url = message.command[1]
    task_id = task_queue.qsize() + 1
    user_id = message.from_user.id
    await task_queue.put((task_id, url, user_id))
    await message.reply_text(f"Task #{task_id} added to queue.")
    # Try to process if not running
    await process_next_task(bot)


@Client.on_message(filters.command("queue") & filters.private)
async def show_queue(bot: Client, message: Message):
    if task_queue.empty():
        await message.reply_text("The task queue is currently empty.")
        return
    tasks = list(task_queue._queue)
    queue_text = "Current task queue:\n" + "\n".join(f"#{t[0]}: {t[1]}" for t in tasks)
    await message.reply_text(queue_text)


@Client.on_message(filters.command("skip") & filters.private)
async def skip_task(bot: Client, message: Message):
    global current_task
    if current_task is None:
        await message.reply_text("No task is currently running.")
        return
    # Cancel current task logic here, for now just clear current task
    await message.reply_text(f"Skipping current task #{current_task[0]}")
    current_task = None
    await process_next_task(bot)


@Client.on_message(filters.command("restart") & filters.private)
async def restart_bot(bot: Client, message: Message):
    await message.reply_text("Restarting bot...")
    await bot.stop()
    # Actual restart logic depends on deployment environment


@Client.on_message(filters.command("cleanup") & filters.private)
async def cleanup(bot: Client, message: Message):
    # Placeholder for cleanup logic, e.g., deleting old files
    await message.reply_text("Cleanup completed.")


@Client.on_message(filters.command("status") & filters.private)
async def status(bot: Client, message: Message):
    queue_length = task_queue.qsize()
    task_info = f"Current running task: #{current_task[0]}" if current_task else "No task running"
    await message.reply_text(f"Queue length: {queue_length}\n{task_info}")


@Client.on_message(filters.command("list") & filters.private)
async def list_tasks(bot: Client, message: Message):
    # List tasks (similar to queue command)
    await show_queue(bot, message)


@Client.on_message(filters.command("settings") & filters.private)
async def settings(bot: Client, message: Message):
    # Placeholder for user settings display
    await message.reply_text("Settings feature is not implemented yet.")

