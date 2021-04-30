import re
import json
from datetime import datetime
from urllib.request import urlopen
from collections import deque

from logging import Logger

from modules.stock import Stock

from telegram import Update
from telegram.ext import (
    Updater,
    Filters,
    CallbackContext,
    MessageHandler,
    CommandHandler,
    JobQueue
)


class Bort:
    '''A module-level docstring

    Notice the comment above the docstring specifying the encoding.
    Docstrings do appear in the bytecode, so you can access this through
    the ``__doc__`` attribute. This is also what you'll see if you call
    help() on a module or any other Python object.
    '''

    BASEURL = "https://query1.finance.yahoo.com/v7/finance/quote?symbols="

    def timeDiff(self, inputTime: datetime) -> int:
        date = inputTime.replace(tzinfo=None)
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
        uniqueSymbols = list(dict.fromkeys(symbols))
        # Get rid of $
        uniqueSymbols = [x[1:] for x in uniqueSymbols]
        uniqueSymbols = ','.join(uniqueSymbols)

        # Yahoo Finance Request
        try:
            with urlopen(self.BASEURL + uniqueSymbols, timeout=10) as response:
                read = response.read()
                read = json.loads(read)
        except:
            self.logger.error(
                f'{user.full_name} [{update.message.from_user.id}]: {uniqueSymbols}')

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
                response, parse_mode='HTML', reply_to_message_id=update.message.message_id)

    def tail(self, update: Update, context: CallbackContext) -> None:
        with open('log.txt') as file:
            tail = deque(file, 10)
        for line in tail:
            update.message.reply_text(line)

    def callback_alarm(self, context: CallbackContext) -> None:
        job = context.job
        context.bot.send_message(job.context, text='Beep!')

    def set_timer(self, update: Update, context: CallbackContext) -> None:
        update.message.reply_text('Timer response')
        chat_id = update.message.chat_id
        context.job_queue.run_repeating(callback=self.callback_alarm,
                                        interval=10,
                                        context=chat_id,
                                        name=str(chat_id))
    
    def state_timer(self, update: Update, context: CallbackContext) -> None:
        name = str(update.message.chat_id)
        current_jobs = context.job_queue.get_jobs_by_name(name)
        if any(current_job.name == name for current_job in current_jobs):
            update.message.reply_text('Currently active')
        else:
            update.message.reply_text('Not active')

    def __init__(self, logger: Logger):
        with open('token.txt', 'r') as f:
            token = f.readline().replace('\n', '')

        # Class vars
        self.logger = logger
        self.updater = Updater(token, use_context=True)

        # Handlers
        dispatcher = self.updater.dispatcher

        start_handler = CommandHandler('start', self.start)
        help_handler = CommandHandler('help', self.helper)
        command_handler = CommandHandler('tail', self.tail)
        set_timer_handler = CommandHandler('setTimer', self.set_timer)
        state_timer_handler = CommandHandler('stateTimer', self.state_timer)
        # message_handler = MessageHandler(Filters.text, self.stock)

        dispatcher.add_handler(start_handler)
        dispatcher.add_handler(help_handler)
        dispatcher.add_handler(command_handler)
        dispatcher.add_handler(set_timer_handler)
        dispatcher.add_handler(state_timer_handler)
        # dispatcher.add_handler(message_handler)

        # Start the Bot
        self.updater.start_polling()

        # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
        # SIGABRT. This should be used most of the time, since start_polling() is
        # non-blocking and will stop the bot gracefully.
        self.updater.idle()
