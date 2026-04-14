import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import FSInputFile, Message

from utils import text
from services.thumbnail_store import ThumbnailStore

router = Router(name="thumbnails")
logger = logging.getLogger(__name__)


@router.message(F.chat.type == "private", F.photo)
async def save_thumbnail(message: Message, thumbnail_store: ThumbnailStore) -> None:
    if not message.from_user:
        return
    largest_photo = message.photo[-1]
    path = thumbnail_store.path_for_user(message.from_user.id)
    await message.bot.download(largest_photo, destination=path)
    logger.info("Thumbnail saved | user=%s path=%s", message.from_user.id, path)
    await message.answer(text.THUMB_SAVED)


@router.message(Command("thumb"), F.chat.type == "private")
async def show_thumbnail(message: Message, thumbnail_store: ThumbnailStore) -> None:
    if not message.from_user:
        return
    thumbnail = thumbnail_store.get(message.from_user.id)
    if not thumbnail:
        logger.info("Thumbnail missing | user=%s", message.from_user.id)
        await message.answer(text.THUMB_MISSING)
        return
    logger.info("Thumbnail shown | user=%s path=%s", message.from_user.id, thumbnail)
    await message.answer_photo(FSInputFile(thumbnail), caption="Your custom thumbnail.")


@router.message(Command("delthumb"), F.chat.type == "private")
async def delete_thumbnail(message: Message, thumbnail_store: ThumbnailStore) -> None:
    if not message.from_user:
        return
    if thumbnail_store.delete(message.from_user.id):
        logger.info("Thumbnail deleted | user=%s", message.from_user.id)
        await message.answer(text.THUMB_REMOVED)
    else:
        logger.info("Thumbnail delete requested but missing | user=%s", message.from_user.id)
        await message.answer(text.THUMB_MISSING)
