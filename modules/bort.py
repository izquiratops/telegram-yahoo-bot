import re, json
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
		rockets: str = '🚀' * floor(self.totalChangePercent / 5)
		message: str = f"🔸 {self.displayName} ${self.symbol.upper()} {rockets}\n"

		# Pre Market
		if 'pre' in self.marketValues:
			if (float(self.marketValues['pre']['ChangePercent']) > 0):
				emoji = '📈'
			else:
				emoji = '📉'
			message +=	f"<b>Pre Market</b> {emoji}\n" \
						f"{self.marketValues['pre']['Price']}$ " \
						f"({self.marketValues['pre']['Change']}$, {self.marketValues['pre']['ChangePercent']}%)\n"

		# Regular Market
		if 'regular' in self.marketValues:
			if (float(self.marketValues['regular']['ChangePercent']) > 0):
				emoji = '📈'
			else:
				emoji = '📉'
			message +=	f"<b>Regular Market</b> {emoji}\n" \
						f"{self.marketValues['regular']['Price']}$ " \
						f"({self.marketValues['regular']['Change']}$, {self.marketValues['regular']['ChangePercent']}%)\n"

		# After hours
		if 'post' in self.marketValues:
			if (float(self.marketValues['post']['ChangePercent']) > 0):
				emoji = '📈'
			else:
				emoji = '📉'
			message +=	f"<b>After Hours</b> {emoji}\n" \
						f"{self.marketValues['post']['Price']}$ " \
						f"({self.marketValues['post']['Change']}$, {self.marketValues['post']['ChangePercent']}%)\n"

		return message

	def __init__(self, obj) -> None:
		# Symbol
		self.symbol = obj['symbol']

		# Stock / Fund name
		if 'displayName' in obj:
			self.displayName = obj['displayName']
		elif 'longName' in obj:
			self.displayName = obj['longName']
		else:
			self.displayName = obj['shortName']

		# 'marketValues' is a dict with 3 keys: Regular, Pre and Post.
		# Each one has Price, Change and ChangePercent
		marketTemplate = ['Price','Change','ChangePercent']
		self.totalChangePercent = 0
		self.marketValues = dict()

		# Regular Market
		regularMarketKeys = ['regularMarketPrice','regularMarketChange','regularMarketChangePercent']
		if obj.keys() >= set(regularMarketKeys):
			self.totalChangePercent += float(obj['regularMarketChangePercent'])
			self.marketValues['regular'] = dict()
			for prop, key in zip(marketTemplate, regularMarketKeys):
				self.marketValues['regular'][prop] = format(round(obj[key], 2))

		# After Hours
		postMarketKeys = ['postMarketPrice','postMarketChange','postMarketChangePercent']
		if obj.keys() >= set(postMarketKeys):
			self.totalChangePercent += float(obj['postMarketChangePercent'])
			self.marketValues['post'] = dict()
			for prop, key in zip(marketTemplate, postMarketKeys):
				self.marketValues['post'][prop] = format(round(obj[key], 2))

		# Pre Market
		preMarketKeys = ['preMarketPrice','preMarketChange','preMarketChangePercent']
		if obj.keys() >= set(preMarketKeys):
			self.totalChangePercent += float(obj['preMarketChangePercent'])
			self.marketValues['pre'] = dict()
			for prop, key in zip(marketTemplate, preMarketKeys):
				self.marketValues['pre'][prop] = format(round(obj[key], 2))

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
			with urlopen(BASEURL + uniqueSymbols, timeout=10) as response:
				read = response.read()
				read = json.loads(read)
		except:
			self.logger.error(f'{user.full_name} [{update.message.from_user.id}]: {uniqueSymbols}')

		# Write bot response
		stocks = []
		for element in read['quoteResponse']['result']:
			stock = Stock(element)
			stocks.append(stock)

		if len(stocks) > 0:
			# Sorted by change value
			# stocks.sort(key=lambda x: x.totalChangePercent, reverse=True)

			# Write Response
			response: str = ''
			for stock in stocks:
				response += f'{stock}\n'
				self.logger.info(f'{user.full_name} [{update.message.from_user.id}]: {stock.symbol}')

			# Reply!
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

