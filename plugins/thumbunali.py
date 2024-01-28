import os
from pyrogram import Client, filters
from config import Config


@Client.on_message(filters.photo & filters.incoming & filters.private)
async def save_photo(_bot, message):
    download_location = f"{Config.DOWNLOAD_LOCATION}/{message.from_user.id}.jpg"
    await message.download(file_name=download_location)

    await message.reply_text(text="your custom thumbnail is saved", quote=True)


@Client.on_message(filters.command("thumb") & filters.incoming & filters.private)
async def send_photo(_bot, message):
    download_location = f"{Config.DOWNLOAD_LOCATION}/{message.from_user.id}.jpg"

    if os.path.isfile(download_location):
        await message.reply_photo(
            photo=download_location, caption="your custom thumbnail", quote=True
        )
    else:
        await message.reply_text(
            text="you don't have set thumbnail yet!. send .jpg img to save as thumbnail.",
            quote=True,
        )


@Client.on_message(filters.command("delthumb") & filters.incoming & filters.private)
async def delete_photo(_bot, message):
    download_location = f"{Config.DOWNLOAD_LOCATION}/{message.from_user.id}.jpg"
    if os.path.isfile(download_location):
        os.remove(download_location)
        await message.reply_text(
            text="your thumbnail removed successfully.", quote=True
        )
    else:
        await message.reply_text(
            text="you don't have set thumbnail yet!. send .jpg img to save as thumbnail.",
            quote=True,
        )
