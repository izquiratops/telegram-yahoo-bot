import re, json
# API Yahoo Finance update
from math import floor
from datetime import datetime
from collections import deque
from logging import Logger
from urllib.request import urlopen

from telegram import Update
from telegram.ext import (
	Updater,
	Filters,
	CallbackContext,
	MessageHandler,
	CommandHandler
)


BASEURL = "https://query1.finance.yahoo.com/v7/finance/quote?symbols="

class Stock:
	def __str__(self) -> str:
		times = floor(float(self.regularMarketChangePercent) / 5)
		if (times > 0):
			rockets: str = '🚀' * times
		else:
			rockets: str = '📉' * times
		message: str = f"🔸 {self.displayName} ${self.symbol.upper()} {rockets}\n"

		# Regular Market 
		message +=	f"<b>Regular Market</b> " \
					f"{self.regularMarketPrice}$ " \
					f"({self.regularMarketChange}$, {self.regularMarketChangePercent}%)\n"

		# Post Market
		try:
			message +=	f"<b>Post Market</b> " \
						f"{self.postMarketPrice}$ " \
						f"({self.postMarketChange}$, {self.postMarketChangePercent}%)\n"
		except:
			pass

		return message

	def __init__(self, obj) -> None:
		# Symbol
		self.symbol = obj['symbol']

		# Name
		if 'displayName' in obj:
			self.displayName = obj['displayName']
		else:
			self.displayName = obj['longName']

		# Regular Market
		self.regularMarketPrice			= format(round(obj['regularMarketPrice'], 2))
		self.regularMarketChange		= format(round(obj['regularMarketChange'], 2))
		self.regularMarketChangePercent	= format(round(obj['regularMarketChangePercent'], 2))

		# Post Market
		if 'postMarketPrice' in obj:
			self.postMarketPrice		 = format(round(obj['postMarketPrice'], 2))
		if 'postMarketChange' in obj:
			self.postMarketChange		 = format(round(obj['postMarketChange'], 2))
		if 'postMarketChangePercent' in obj:
			self.postMarketChangePercent = format(round(obj['postMarketChangePercent'], 2))

class Bort:
	'''A module-level docstring

	Notice the comment above the docstring specifying the encoding.
	Docstrings do appear in the bytecode, so you can access this through
	the ``__doc__`` attribute. This is also what you'll see if you call
	help() on a module or any other Python object.
	'''

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
		# Ignore message edits AND requests older than 5 mins
		if not update.message and self.timeDiff(update.message.date) > 5:
			return

		# Ignore message if has no symbols on it
		symbols = re.findall('[$][^\\s]*', update.message.text)
		if len(symbols) == 0:
			return

		# Get User for log porposes
		user = update.message.from_user
		# List of unique symbols
		uniqueSymbols = list(dict.fromkeys(symbols))
		uniqueSymbols = [x[1:] for x in uniqueSymbols] # Get rid of $
		uniqueSymbols = ','.join(uniqueSymbols)

		# Yahoo Finance Request
		try:
			with urlopen(BASEURL + uniqueSymbols) as response:
				read = response.read()
				read = json.loads(read)
		except:
			self.logger.error(f'{user.full_name} - {update.message.from_user.id} - Symbols: {uniqueSymbols}')

		# Write bot response
		response: str = ''
		for element in read['quoteResponse']['result']:
			stock = Stock(element)
			response += f'{stock}\n'
			self.logger.info(f'{user.full_name} - {update.message.from_user.id} - {stock.symbol}')

		if response:
			update.message.reply_text(response, parse_mode='HTML', reply_to_message_id=update.message.message_id)

	def tail(self, update: Update, context: CallbackContext) -> None:
		with open('log.txt') as fin:
			tail = deque(fin, 10)
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

