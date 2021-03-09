from logging import Logger
from collections import deque
from telegram import Update
from telegram.ext import (
	Updater,
	Filters,
	CallbackContext,
	MessageHandler,
	CommandHandler
)

import re
from modules.scraper import Scraper
from modules.utils import Utils

class Bort:
	'''A module-level docstring

	Notice the comment above the docstring specifying the encoding.
	Docstrings do appear in the bytecode, so you can access this through
	the ``__doc__`` attribute. This is also what you'll see if you call
	help() on a module or any other Python object.
	'''

	def start(self, update: Update, context: CallbackContext) -> None:
		update.message.reply_text(
			'<i>You can’t beat the market but you can beat your meat</i>\n\n'
			'- Warren Buffet probably',
			parse_mode='HTML')

	def helper(self, update: Update, context: CallbackContext) -> None:
		update.message.reply_text(
			"<b>/start</b> - Greetings from Bort\n"
			"<b>/help</b> - You're currently here\n"
			"<b>/<i>insert_symbol_here</i></b> - Ask for the price of a stock\n",
			parse_mode='HTML'
		)

	def stock(self, update: Update, context: CallbackContext) -> None:
		if not update.message:
			return

		user = update.message.from_user
		symbols = re.findall('[$][^\\s]*', update.message.text)
		unique = list(dict.fromkeys(symbols))

		# Requesting data
		response = ""
		for symbol in unique:
			try:
				message = self.scraper.getFromStock(symbol[1:])
				response += f'{message}\n'
				self.logger.info(f'{user.full_name} ({user.id}) -> {symbol}')
			except Exception as e:
				self.logger.error(f'{user.full_name} ({user.id}) -> {symbol}: {e}')

		# Response
		if response:
			update.message.reply_text(response, reply_to_message_id=update.message.message_id)

	def tail(self, update: Update, context: CallbackContext) -> None:
		with open('log.txt') as fin:
			tail = deque(fin, 10)
		update.message.reply_text(''.join(tail))


	def __init__(self, logger: Logger):
		with open('token.txt', 'r') as f:
			token = f.readline().replace('\n', '')

		# Class vars
		self.logger = logger
		self.updater = Updater(token, use_context=True)

		# Project Modules
		self.scraper = Scraper()
		self.utils = Utils()

		# Handlers
		dispatcher = self.updater.dispatcher

		dispatcher.add_handler(CommandHandler('start', self.start))
		dispatcher.add_handler(CommandHandler('help', self.helper))
		dispatcher.add_handler(CommandHandler('tail', self.tail))
		dispatcher.add_handler(MessageHandler(Filters.regex('[$][^\\s]*'), self.stock))

