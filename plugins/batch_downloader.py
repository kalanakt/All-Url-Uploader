import os
import mimetypes
from pyrogram import Client, filters
from pyrogram.types import Message
import asyncio
import re

MAX_LIMIT = 200

user_state = {}
user_data = {}

@Client.on_message(filters.command("batch") & filters.private)
async def batch_start(client, message):
    user_id = message.from_user.id
    user_state[user_id] = "waiting_link"
    await message.reply_text("Send me the starting Telegram message link (e.g. https://t.me/c/2993579763/2654/2655).")

@Client.on_message(filters.private)
async def batch_handler(client, message):
    user_id = message.from_user.id
    text = message.text.strip()

    if user_state.get(user_id) == "waiting_link":
        m = re.match(r"https://t.me/c/(d+)/(d+)/(d+)", text)
        if not m:
            await message.reply_text("Invalid link format. Example: https://t.me/c/2993579763/2654/2655")
            return
        
        chat_id = int("-100" + m.group(1))
        start_msg_id = int(m.group(3))
        user_data[user_id] = {"chat_id": chat_id, "start_msg_id": start_msg_id}
        
        user_state[user_id] = "waiting_count"
        await message.reply_text(f"How many files do you want to download starting from this message? (max {MAX_LIMIT})")

    elif user_state.get(user_id) == "waiting_count":
        try:
            count = int(text)
            if count < 1 or count > MAX_LIMIT:
                raise ValueError()
        except ValueError:
            await message.reply_text(f"Please provide a number between 1 and {MAX_LIMIT}.")
            return
        
        user_data[user_id]["count"] = count
        user_state[user_id] = "downloading"

        status_msg = await message.reply_text(f"Starting downloads: 0/{count}")
        await client.pin_chat_message(message.chat.id, status_msg.message_id)

        completed = 0
        chat_id = user_data[user_id]["chat_id"]
        current_msg_id = user_data[user_id]["start_msg_id"]

        for _ in range(count):
            try:
                msg = await client.get_messages(chat_id, current_msg_id)
                if msg and msg.media:
                    file_path = await client.download_media(msg)
                    mime_type, _ = mimetypes.guess_type(file_path)
                    if mime_type:
                        if mime_type.startswith("video/"):
                            await client.send_video(message.chat.id, file_path)
                        elif mime_type == "application/pdf":
                            await client.send_document(message.chat.id, file_path)
                        elif mime_type.startswith("text/") or mime_type == "text/html":
                            # For text or html files, send as text message content
                            with open(file_path, "r", encoding="utf-8") as f:
                                content = f.read()
                            await client.send_message(message.chat.id, content)
                        else:
                            # fallback: send as document
                            await client.send_document(message.chat.id, file_path)
                    else:
                        # unknown mime, send as document
                        await client.send_document(message.chat.id, file_path)

                    # Optionally delete file after sending to free disk space
                    os.remove(file_path)

                completed += 1
                await status_msg.edit_text(f"Downloading files: {completed}/{count}")
            except Exception as e:
                await status_msg.edit_text(f"Error downloading message {current_msg_id}: {str(e)}")
            current_msg_id += 1

        await client.unpin_chat_message(message.chat.id, status_msg.message_id)
        await status_msg.edit_text("All downloads completed!")
        user_state[user_id] = None
        user_data[user_id] = None