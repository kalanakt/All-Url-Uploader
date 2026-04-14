from __future__ import annotations

import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import Settings
from utils.logging_config import setup_logging
from routers.callbacks import router as callbacks_router
from routers.commands import router as commands_router
from routers.intake import router as intake_router
from routers.thumbnails import router as thumbnails_router
from services.cooldown import CooldownManager
from services.request_store import RequestStore
from services.thumbnail_store import ThumbnailStore


def create_dispatcher(settings: Settings) -> Dispatcher:
    dispatcher = Dispatcher()
    dispatcher.include_router(commands_router)
    dispatcher.include_router(thumbnails_router)
    dispatcher.include_router(intake_router)
    dispatcher.include_router(callbacks_router)
    dispatcher.workflow_data.update(
        settings=settings,
        cooldown=CooldownManager(timeout_seconds=settings.process_max_timeout),
        request_store=RequestStore(settings.requests_dir, settings.work_dir),
        thumbnail_store=ThumbnailStore(settings.thumbnails_dir),
    )
    return dispatcher


async def run() -> None:
    setup_logging()
    settings = Settings.from_env()
    settings.ensure_directories()

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dispatcher = create_dispatcher(settings)

    logging.getLogger(__name__).info(
        "Bot is starting | download_dir=%s requests_dir=%s proxy=%s cooldown=%ss",
        settings.download_location,
        settings.requests_dir,
        "enabled" if settings.http_proxy else "disabled",
        settings.process_max_timeout,
    )
    await dispatcher.start_polling(bot)
