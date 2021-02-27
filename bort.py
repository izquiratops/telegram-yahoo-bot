from logging import Logger
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Dispatcher, Updater, CallbackContext, CommandHandler, CallbackQueryHandler

# Project modules
from modules.scraper import Scraper
from modules.utils import Utils

SCRAPER = Scraper()
UTILS = Utils()

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
		update.message.reply_text('/stock *your symbol here*')

	def stockCommand(self, update: Update, context: CallbackContext) -> None:
		# Any comment older than 5 minutes ago will be ignored
		if UTILS.timeDiff(update.message.date) > 5:
			return

		# Getting symbol and scrapping the web
		try:
			symbol = UTILS.getSymbol(update.message.text)
			message = SCRAPER.getFromStock(symbol)
		except Exception as e:
			# Report error
			self.logger.error(f'{update.effective_chat.full_name} ({update.effective_chat.id})\n{e}')
			update.message.reply_text(e.args[0], reply_to_message_id=update.message.message_id)

		# Sending message
		self.logger.info(f'{update.effective_chat.full_name} ({update.effective_chat.id}) -> {symbol}')
		update.message.reply_text(message, reply_to_message_id=update.message.message_id)

	def addFavorite(self, update: Update, context: CallbackContext) -> None:
		update.message.reply_text('addFav command working')

	def favorites(self, update: Update, context: CallbackContext) -> None:
		keyboard = [
			[
				InlineKeyboardButton('Baba', callback_data='baba'),
				InlineKeyboardButton('Gamestock', callback_data='gme')
			],
			[
				InlineKeyboardButton('Norwegian', callback_data='nclh')
			]
		]

		replyMarkup = InlineKeyboardMarkup(keyboard)
		update.message.reply_text('Select stock:', reply_markup=replyMarkup)

	def stockCallback(self, update: Update, context: CallbackContext) -> None:
		# CallbackQueries need to be answered, even if no notification to the user is needed
		# Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
		query = update.callback_query
		query.answer()

		# Getting symbol and scrapping the web
		try:
			message = SCRAPER.getFromStock(query.data)
		except Exception as e:
			# Report error
			self.logger.error(f'{update.effective_chat.full_name} ({update.effective_chat.id})\n{e}')
			update.message.reply_text(e.args[0], reply_to_message_id=update.message.message_id)

		query.edit_message_text(f'Stock: {query.data.upper()}\n{message}')

	def __init__(self, logger: Logger):
		with open('token.txt', 'r') as f:
			token = f.readline().replace('\n', '')
		assert token is not None, 'Couldn\'t read the token'

		# Class vars
		self.logger = logger
		self.updater = Updater(token, use_context=True)

		# Handlers
		dispatcher = self.updater.dispatcher
		dispatcher.add_handler(CommandHandler('start', 	self.start))
		dispatcher.add_handler(CommandHandler('help', 	self.helper))
		dispatcher.add_handler(CommandHandler('stock', 	self.stockCommand))
		dispatcher.add_handler(CommandHandler('addFav', self.addFavorite))
		dispatcher.add_handler(CommandHandler('favs', 	self.favorites))
		dispatcher.add_handler(CallbackQueryHandler(self.stockCallback))
