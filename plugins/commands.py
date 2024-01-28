from pyrogram import Client, filters
from pyrogram.types import Message
from plugins.script import Translation


@Client.on_message(
    filters.command("start") & filters.private,
)
async def start_bot(_bot, m: Message):
    return await m.reply_text(
        Translation.START_TEXT.format(m.from_user.first_name),
        reply_markup=Translation.START_BUTTONS,
        disable_web_page_preview=True,
        quote=True,
    )


@Client.on_message(
    filters.command("help") & filters.private,
)
async def help_bot(_bot, m: Message):
    return await m.reply_text(
        Translation.HELP_TEXT,
        reply_markup=Translation.HELP_BUTTONS,
        disable_web_page_preview=True,
    )


@Client.on_message(
    filters.command("about") & filters.private,
)
async def aboutme(_bot, m: Message):
    return await m.reply_text(
        Translation.ABOUT_TEXT,
        reply_markup=Translation.ABOUT_BUTTONS,
        disable_web_page_preview=True,
    )
