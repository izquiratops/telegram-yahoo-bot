# Python imports
import re
import json
from math import floor
from datetime import datetime
from urllib.request import urlopen
from dataclasses import dataclass
from collections import deque

# Logger
from logging import Logger

# Telegram API
from telegram import Update
from telegram.ext import (
    Updater,
    Filters,
    CallbackContext,
    MessageHandler,
    CommandHandler
)


@dataclass
class Stock:
    symbol: str
    displayName: str
    totalChangePercent: float

    regularMarketPrice: float
    regularMarketChange: float
    regularMarketChangePercent: float

    postMarketPrice: float
    postMarketChange: float
    postMarketChangePercent: float

    preMarketPrice: float
    preMarketChange: float
    preMarketChangePercent: float

    def __str__(self) -> str:
        rockets: str = '🚀' * floor(self.totalChangePercent / 5)
        message: str = f"🔸 {self.displayName} ${self.symbol.upper()} {rockets}\n"

        if 'preMarketPrice' in dir(self):
            if (float(self.preMarketChangePercent) > 0):
                emoji = '📈'
            else:
                emoji = '📉'
            message += f"<b>Pre Market</b> {emoji}\n" \
                f"{self.preMarketPrice}$ " \
                f"({self.preMarketChange}$, {self.preMarketChangePercent}%)\n"

        if 'regularMarketPrice' in dir(self):
            if (float(self.regularMarketChangePercent) > 0):
                emoji = '📈'
            else:
                emoji = '📉'
            message += f"<b>Regular Market</b> {emoji}\n" \
                f"{self.regularMarketPrice}$ " \
                f"({self.regularMarketChange}$, {self.regularMarketChangePercent}%)\n"

        if 'postMarketPrice' in dir(self):
            if (float(self.postMarketChangePercent) > 0):
                emoji = '📈'
            else:
                emoji = '📉'
            message += f"<b>After Hours</b> {emoji}\n" \
                f"{self.postMarketPrice}$ " \
                f"({self.postMarketChange}$, {self.postMarketChangePercent}%)\n"

        return message

    def __init__(self, obj) -> None:
        self.symbol = obj['symbol']
        self.displayName = obj['displayName'] or obj['longName'] or obj['shortName']
        self.totalChangePercent = 0

        if 'regularMarketPrice' in obj:
            self.regularMarketPrice = format(
                round(obj['regularMarketPrice'], 2))
            self.regularMarketChange = format(
                round(obj['regularMarketChange'], 2))
            self.regularMarketChangePercent = format(
                round(obj['regularMarketChangePercent'], 2))
            self.totalChangePercent += float(obj['regularMarketChangePercent'])

        if 'postMarketPrice' in obj:
            self.postMarketPrice = format(
                round(obj['postMarketPrice'], 2))
            self.postMarketChange = format(
                round(obj['postMarketChange'], 2))
            self.postMarketChangePercent = format(
                round(obj['postMarketChangePercent'], 2))
            self.totalChangePercent += float(obj['postMarketChangePercent'])

        if 'preMarketPrice' in obj:
            self.preMarketPrice = format(
                round(obj['preMarketPrice'], 2))
            self.preMarketChange = format(
                round(obj['preMarketChange'], 2))
            self.preMarketChangePercent = format(
                round(obj['preMarketChangePercent'], 2))
            self.totalChangePercent += float(obj['preMarketChangePercent'])


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

    def __init__(self, logger: Logger):
        with open('token.txt', 'r') as f:
            token = f.readline().replace('\n', '')

        # Class vars
        self.logger = logger
        self.updater = Updater(token, use_context=True)

        # Handlers
        dispatcher = self.updater.dispatcher
        dispatcher.add_handler(CommandHandler('start', self.start))
        dispatcher.add_handler(CommandHandler('help', self.helper))
        dispatcher.add_handler(CommandHandler('tail', self.tail))
        dispatcher.add_handler(MessageHandler(Filters.text, self.stock))
