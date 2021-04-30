import re
import json
from datetime import datetime
from urllib.request import urlopen
from collections import deque

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Updater,
    Filters,
    CallbackContext,
    MessageHandler,
    CommandHandler,
    ConversationHandler,
    JobQueue
)

from modules.stock import Stock
from modules.alerts import AlertService

from logging import Logger


SETTING_VALUE = range(1)
BASEURL = "https://query1.finance.yahoo.com/v7/finance/quote?symbols="


class Bort:
    '''A module-level docstring

    Notice the comment above the docstring specifying the encoding.
    Docstrings do appear in the bytecode, so you can access this through
    the ``__doc__`` attribute. This is also what you'll see if you call
    help() on a module or any other Python object.
    '''

    def timeDiff(self, input_time: datetime) -> int:
        date = input_time.replace(tzinfo=None)
        now = datetime.utcnow()
        return (now - date).total_seconds() / 60

    def start(self, update: Update, context: CallbackContext) -> None:
        update.message.reply_text(
            '<i>You can’t beat the market but you can beat your meat</i>\n\n'
            '- Warren Buffet probably',
            parse_mode='HTML')

    def helper(self, update: Update, context: CallbackContext) -> None:
        update.message.reply_text(
            "<b>/start</b> - Greetings from Bort\n"
            "<b>/help</b> - You're currently here\n"
            "<b>... $<i>insert_symbol_here</i></b> ... - Ask for the price of a stock\n",
            parse_mode='HTML'
        )

    def tail(self, update: Update, context: CallbackContext) -> None:
        with open('log.txt') as file:
            tail = deque(file, 10)
        for line in tail:
            update.message.reply_text(line)

    def stock(self, update: Update, context: CallbackContext) -> None:
        # Ignore message edits OR requests older than 5 mins
        if not update.message or self.timeDiff(update.message.date) > 5:
            return

        # Ignore message if has no symbols on it
        symbols = re.findall('[$][^\\s]*', update.message.text)
        if len(symbols) == 0:
            return

        # Get User for log porposes
        user = update.message.from_user
        # List of unique symbols
        unique_symbols = list(dict.fromkeys(symbols))
        # Get rid of $
        unique_symbols = [x[1:] for x in unique_symbols]
        unique_symbols = ','.join(unique_symbols)

        # Yahoo Finance Request
        try:
            with urlopen(BASEURL + unique_symbols, timeout=10) as response:
                read = response.read()
                read = json.loads(read)
        except:
            self.logger.error(
                f'{user.full_name} [{update.message.from_user.id}]: {unique_symbols}')

        # Write Response
        response: str = ''
        for element in read['quoteResponse']['result']:
            stock = Stock(element)
            response += f'{stock}\n'
            self.logger.info(
                f'{user.full_name} [{update.message.from_user.id}]: {stock.symbol}')

        # Reply!
        if (response != ''):
            update.message.reply_text(
                response,
                parse_mode='HTML',
                reply_to_message_id=update.message.message_id)

    def callback_alert(self, context: CallbackContext) -> None:
        job = context.job
        context.bot.send_message(job.context, text='Beep!')

    def enable_alerts(self, update: Update, context: CallbackContext) -> None:
        update.message.reply_text('Notifications activated 🎉🥳')

        chat_id = update.message.chat_id
        context.job_queue.run_repeating(callback=self.callback_alert,
                                        interval=10,
                                        context=chat_id,
                                        name=str(chat_id))

    def disable_alerts(self, update: Update, context: CallbackContext) -> None:
        update.message.reply_text('Any alert won\'t be notified anymore 🤫')

        name = str(update.message.chat_id)
        current_jobs = context.job_queue.get_jobs_by_name(name)
        for current_job in current_jobs:
            current_job.schedule_removal()

    def state_alerts(self, update: Update, context: CallbackContext) -> None:
        name = str(update.message.chat_id)
        current_jobs = context.job_queue.get_jobs_by_name(name)
        if current_jobs:
            update.message.reply_text('Currently active')
        else:
            update.message.reply_text('Not active')

        # TODO: List every alarm from this chat_id

    def asking_new_alert(self, update: Update, _: CallbackContext) -> int:
        update.message.reply_text(
			'Tell me which symbol and price like this: $AAPL 250.50 \nOr use the <b>/cancel</b> command.',
			parse_mode='HTML', 
			reply_to_message_id=update.message.message_id)

        return SETTING_VALUE

    def setting_new_alert(self, update: Update, _: CallbackContext) -> int:
        update.message.reply_text('Done! 🎉',
			reply_to_message_id=update.message.message_id)

        return ConversationHandler.END

    def cancel_new_alert(self, update: Update, _: CallbackContext) -> int:
        update.message.reply_text('I\'m not longer waiting for a response',
			reply_to_message_id=update.message.message_id)

        return ConversationHandler.END

    def __init__(self, logger: Logger):
        with open('token.txt', 'r') as file:
            token = file.readline().replace('\n', '')

        # Class vars
        self.logger = logger
        self.updater = Updater(token, use_context=True)

        # Alert class to get access into the db
        self.alert_service = AlertService()

        # Handlers
        dispatcher = self.updater.dispatcher

        start_handler = CommandHandler('start', self.start)
        help_handler = CommandHandler('help', self.helper)
        command_handler = CommandHandler('tail', self.tail)
        enable_alerts_handler = CommandHandler('enableAlerts', self.enable_alerts)
        remove_alerts_handler = CommandHandler('disableAlerts', self.disable_alerts)
        state_alerts_handler = CommandHandler('stateAlerts', self.state_alerts)
        create_new_alert_handler = ConversationHandler(
            entry_points=[CommandHandler('createAlert', self.asking_new_alert)],
            states={ SETTING_VALUE: [MessageHandler(Filters.regex('[$][^\\s]*'), self.setting_new_alert)] },
            fallbacks=[CommandHandler('cancel', self.cancel_new_alert)]
        )
        message_handler = MessageHandler(Filters.text, self.stock)

        dispatcher.add_handler(start_handler)
        dispatcher.add_handler(help_handler)
        dispatcher.add_handler(command_handler)
        dispatcher.add_handler(enable_alerts_handler)
        dispatcher.add_handler(remove_alerts_handler)
        dispatcher.add_handler(state_alerts_handler)
        dispatcher.add_handler(create_new_alert_handler)
        dispatcher.add_handler(message_handler)
