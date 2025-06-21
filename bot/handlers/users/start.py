from logging import Logger

from aiogram.types import Message, User
from aiogram.utils.markdown import hbold


async def command_start_handler(
    message: Message,
    log: Logger,
    event_from_user: User,
) -> None:
    """
    This handler receives messages with `/start` command
    """
    log.info("[%s] %s: нажал старт", event_from_user.id, event_from_user.full_name)

    # Most event objects have aliases for API methods that can be called in events' context
    # For example if you want to answer to incoming message you can use `message.answer(...)` alias
    # and the target chat will be passed to :ref:`aiogram.methods.send_message.SendMessage`
    # method automatically or call API method directly via
    # Bot instance: `bot.send_message(chat_id=message.chat.id, ...)`
    await message.answer(f"Hello, {hbold(event_from_user.full_name)}!")
