import random
from logging import Logger

from telegram import Update
from telegram.ext import (CallbackContext, CommandHandler)
from telegram.ext.updater import Updater

from modules.database import DatabaseService


class BotHandlers:
    QUTOES = [
        '<i>You can’t beat the market but you can beat your meat</i>\n\n- Warren Buffet probably',
        '<i>¡Viva el vino de Ribeiro!</i>\n\n- Mariano Rajoy'
    ]

    def start(self, update: Update, _: CallbackContext) -> None:
        update.message.reply_text(
            text=random.choice(self.QUTOES),
            parse_mode='HTML')

    def helper(self, update: Update, _: CallbackContext) -> None:
        update.message.reply_text(
            text='<b>/start</b> - Greetings from Bort\n'
            '<b>/help</b> - You\'re currently here\n'
            '<b>... $<i>insert_symbol_here</i></b> ... - Ask for the price of a stock\n',
            parse_mode='HTML')

    def __init__(self, logger: Logger, database: DatabaseService, updater: Updater) -> None:
        self.logger = logger
        self.database = database

        # Handlers
        start = CommandHandler('start', self.start)
        helper = CommandHandler('help', self.helper)

        # Dispatcher
        dispatcher = updater.dispatcher
        dispatcher.add_handler(start)
        dispatcher.add_handler(helper)
