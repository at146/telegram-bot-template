from aiogram import Router
from aiogram.filters import CommandStart

from bot.handlers.users import start


def prepare_router() -> Router:
    router = Router(name="router")
    # start
    router.message.register(start.command_start_handler, CommandStart())

    return router
