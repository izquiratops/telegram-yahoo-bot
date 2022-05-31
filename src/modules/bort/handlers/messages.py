import re
from logging import Logger
from datetime import datetime

from telegram import Update
from telegram.ext import CallbackContext
from telegram.ext.filters import Filters
from telegram.ext.messagehandler import MessageHandler

from modules.httpRequests import *
from modules.database import DatabaseService
from modules.updater import UpdaterService
from modules.model.stock import Stock


class MessageHandlers:
    def _minutes_difference(self, input_time: datetime) -> int:
        date = input_time.replace(tzinfo=None)
        now = datetime.utcnow()
        return (now - date).total_seconds() / 60

    def regex_message(self, update: Update, _: CallbackContext) -> None:
        print(f'->>> {update.message.chat_id}')

        # Ignore message edits OR requests older than 5 mins
        if not update.message or self._minutes_difference(update.message.date) > 5:
            return

        # Ignore message if has no symbols on it
        symbols = re.findall('[$][^\\s]*', update.message.text)
        if len(symbols) == 0:
            return

        # List of unique symbols
        unique_symbols = list(dict.fromkeys(symbols))

        # Get rid of '$' chars
        unique_symbols = [x.replace('$', '') for x in unique_symbols]

        # Yahoo Finance Request
        user = update.message.from_user
        response = None
        try:
            response = request_stocks(unique_symbols)
        except ConnectionError as error:
            self.logger.error(
                f'{user.full_name} '
                f'[{update.message.from_user.id}]: '
                f'{unique_symbols}\n'
                f'{error.args[0].code}: {error.args[0].msg}')
            return

        # Write Response
        response_text = ''
        for element in response:
            stock = Stock(element)
            response_text += f'{stock}\n'
            self.logger.info(
                f'{user.full_name} '
                f'[{update.message.from_user.id}]: '
                f'{stock.symbol}')

        # Reply
        if (response_text != ''):
            update.message.reply_text(
                text=response_text,
                parse_mode='HTML',
                disable_web_page_preview=True,
                reply_to_message_id=update.message.message_id)

    def __init__(self, logger: Logger, db_service: DatabaseService, updater_service: UpdaterService) -> None:
        self.logger = logger
        self.database = db_service
        self.updater = updater_service.updater

        # Handlers
        message = MessageHandler(Filters.text, self.regex_message)

        # Dispatcher
        dispatcher = self.updater.dispatcher
        dispatcher.add_handler(message)
