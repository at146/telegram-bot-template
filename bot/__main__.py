from collections.abc import AsyncGenerator
from typing import Any

from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiohttp.web_app import Application

from bot import handlers
from bot.core.config import settings
from bot.init import bot, log
from bot.runners import run_polling, run_webhook


async def lifespan(app: Application) -> AsyncGenerator[None, Any]:
    dispatcher: Dispatcher = app["main_dp"]

    if settings.ENVIRONMENT != "production":
        log.info("Режим: Debug")

    main_bot_url = f"{settings.MAIN_WEBHOOK_ADDRESS}{settings.MAIN_BOT_PATH}"
    url_main = main_bot_url.format(bot_token=settings.BOT_TOKEN)
    used_update_types = dispatcher.resolve_used_update_types()
    log.info("Used update types: %s", used_update_types)
    log.info("Configuring webhook")
    await bot.set_webhook(
        url=url_main,
        allowed_updates=used_update_types,
        secret_token=settings.MAIN_WEBHOOK_SECRET_TOKEN,
    )
    log.info("Set webhook main - %s", url_main)
    log.info("Configured webhook")

    info_bot = await bot.get_me()
    log.info("<Бот @%s запущен>", info_bot.username)

    yield

    # log.info("Removing webhook")
    # await bot.delete_webhook()
    # log.info("Webhook removed")

    log.info("Stopping bot")
    # Close aiohttp session
    await bot.session.close()
    log.info("Stopped bot")


def main() -> None:
    storage = MemoryStorage()
    main_bot_dispatcher = Dispatcher(storage=storage, log=log)
    main_bot_dispatcher.include_router(handlers.prepare_router())
    # dp.errors.register(error_handler.errors_handler)

    if settings.USE_WEBHOOK:
        run_webhook(dispatcher=main_bot_dispatcher, bot=bot, settings=settings)
    else:
        run_polling(dispatcher=main_bot_dispatcher, bot=bot, log=log)


if __name__ == "__main__":
    main()
