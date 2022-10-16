from logging import Logger

from ..telegramBot import TelegramBot
from .handlers.bot import BotHandlers
from .handlers.messages import MessageHandlers


class Bort:
    def __init__(self, logger: Logger, telegram_bot: TelegramBot) -> None:
        # Commands
        BotHandlers(logger, telegram_bot)

        # Check commands first, then message regex
        MessageHandlers(logger, telegram_bot)

        # Run it 👽
        telegram_bot.start()
