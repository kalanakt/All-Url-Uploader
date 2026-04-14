from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, LinkPreviewOptions, Message

from utils.keyboards import about_keyboard, help_keyboard, start_keyboard
from utils import text

router = Router(name="commands")


async def _send_start(target: Message, name: str) -> None:
    await target.answer(
        text.START_TEXT.format(name=name),
        reply_markup=start_keyboard(),
        link_preview_options=LinkPreviewOptions(is_disabled=True),
    )


@router.message(Command("start"), F.chat.type == "private")
async def start_command(message: Message) -> None:
    first_name = message.from_user.first_name if message.from_user else "there"
    await _send_start(message, first_name)


@router.message(Command("help"), F.chat.type == "private")
async def help_command(message: Message) -> None:
    await message.answer(
        text.HELP_TEXT,
        reply_markup=help_keyboard(),
        link_preview_options=LinkPreviewOptions(is_disabled=True),
    )


@router.message(Command("about"), F.chat.type == "private")
async def about_command(message: Message) -> None:
    await message.answer(
        text.ABOUT_TEXT,
        reply_markup=about_keyboard(),
        link_preview_options=LinkPreviewOptions(is_disabled=True),
    )


async def handle_ui_callback(callback: CallbackQuery, action: str) -> None:
    if not callback.message:
        await callback.answer()
        return

    if action == "home":
        name = callback.from_user.first_name if callback.from_user else "there"
        await callback.message.edit_text(
            text.START_TEXT.format(name=name),
            reply_markup=start_keyboard(),
            link_preview_options=LinkPreviewOptions(is_disabled=True),
        )
    elif action == "help":
        await callback.message.edit_text(
            text.HELP_TEXT,
            reply_markup=help_keyboard(),
            link_preview_options=LinkPreviewOptions(is_disabled=True),
        )
    elif action == "about":
        await callback.message.edit_text(
            text.ABOUT_TEXT,
            reply_markup=about_keyboard(),
            link_preview_options=LinkPreviewOptions(is_disabled=True),
        )
    elif action == "close":
        await callback.message.delete()

    await callback.answer()
