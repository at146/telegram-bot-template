from logging import Logger

from aiogram import Bot, Dispatcher, loggers
from aiogram.webhook import aiohttp_server as server
from aiohttp import web

from bot.core.config import Settings, settings


async def polling_startup(dispatcher: Dispatcher, bot: Bot, log: Logger) -> None:
    if settings.ENVIRONMENT != "production":
        log.info("Режим: Debug")

    await bot.delete_webhook(drop_pending_updates=settings.DROP_PENDING_UPDATES)
    if settings.DROP_PENDING_UPDATES:
        loggers.dispatcher.info("Updates skipped successfully")

    info_bot = await bot.get_me()
    log.info("<Бот @%s запущен>", info_bot.username)


async def polling_shutdown(dispatcher: Dispatcher) -> None:
    pass


async def webhook_startup(dispatcher: Dispatcher, bot: Bot, log: Logger) -> None:
    if settings.ENVIRONMENT != "production":
        log.info("Режим: Debug")

    main_bot_url = f"{settings.MAIN_WEBHOOK_ADDRESS}{settings.MAIN_BOT_PATH}"
    url_main = main_bot_url.format(bot_token=settings.BOT_TOKEN)
    used_update_types = dispatcher.resolve_used_update_types()
    log.info("Used update types: %s", used_update_types)
    log.info("Configuring webhook")
    if await bot.set_webhook(
        url=url_main,
        allowed_updates=used_update_types,
        secret_token=settings.MAIN_WEBHOOK_SECRET_TOKEN,
    ):
        log.info("Set webhook main - %s", url_main)
        log.info("Configured webhook")

        info_bot = await bot.get_me()
        log.info("<Бот @%s запущен>", info_bot.username)
    else:
        loggers.webhook.error("Failed to set main bot webhook on url '%s'", url_main)


async def webhook_shutdown(bot: Bot, log: Logger) -> None:
    if settings.RESET_WEBHOOK:
        if await bot.delete_webhook():
            loggers.webhook.info("Dropped main bot webhook.")
        else:
            loggers.webhook.error("Failed to drop main bot webhook.")
    log.info("Stopping bot")
    # Close aiohttp session
    await bot.session.close()
    log.info("Stopped bot")


def run_polling(dispatcher: Dispatcher, bot: Bot, log: Logger) -> None:
    dispatcher.startup.register(polling_startup)
    dispatcher.shutdown.register(polling_shutdown)
    used_update_types = dispatcher.resolve_used_update_types()
    log.info("Used update types: %s", used_update_types)
    return dispatcher.run_polling(
        bot,
        allowed_updates=used_update_types,
    )


def run_webhook(dispatcher: Dispatcher, bot: Bot, settings: Settings) -> None:
    app: web.Application = web.Application()
    server.SimpleRequestHandler(
        dispatcher=dispatcher,
        bot=bot,
        secret_token=settings.MAIN_WEBHOOK_SECRET_TOKEN,
    ).register(app, path=settings.MAIN_BOT_PATH)

    server.setup_application(app, dispatcher, bot=bot)
    app.update(**dispatcher.workflow_data, bot=bot)
    dispatcher.startup.register(webhook_startup)
    dispatcher.shutdown.register(webhook_shutdown)
    return web.run_app(
        app=app,
        host=settings.MAIN_WEBHOOK_LISTENING_HOST,
        port=settings.MAIN_WEBHOOK_LISTENING_PORT,
    )
