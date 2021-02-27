from logging import Logger
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Dispatcher, Updater, CallbackContext, CommandHandler, CallbackQueryHandler

from modules.database import Database
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
			"<b>/stock</b> <i>symbol</i> - Request stock\n"
			"<b>/addFav</b> <i>symbol</i> - Add stock on the Favorite list\n"
			"<b>/removeFav</b> <i>symbol</i> - Remove stock of the Favorite list\n"
			"<b>/favs</b> - Show Favorite list",
			parse_mode='HTML'
		)

	def stockCommand(self, update: Update, context: CallbackContext) -> None:
		# Any comment older than 5 minutes ago will be ignored
		if self.utils.timeDiff(update.message.date) > 5:
			return

		# Getting symbol and scrapping the web
		try:
			symbol = self.utils.getSymbol(update.message.text)
			message = self.scraper.getFromStock(symbol)
		except Exception as e:
			# Report error (as a Reply)
			self.logger.error(f'{update.effective_chat.full_name} ({update.effective_chat.id})\n{e}')
			update.message.reply_text(e.args[0], reply_to_message_id=update.message.message_id)
			return

		# Sending message
		self.logger.info(f'{update.effective_chat.full_name} ({update.effective_chat.id}) -> {symbol}')
		update.message.reply_text(message, reply_to_message_id=update.message.message_id)

	def addFavorite(self, update: Update, context: CallbackContext) -> None:
		try:
			symbol = self.utils.getSymbol(update.message.text)
			self.db.insertFavorite(update.effective_user.id, symbol)
		except Exception as e:
			# Report error (as a Reply)
			self.logger.error(f'{update.effective_chat.full_name} ({update.effective_chat.id})\n{e}')
			update.message.reply_text(e.args[0], reply_to_message_id=update.message.message_id)
			return

		update.message.reply_text(f'Symbol {symbol} added successfully')

	def removeFavorite(self, update: Update, context: CallbackContext) -> None:
		try:
			symbol = self.utils.getSymbol(update.message.text)
			self.db.deleteFavorite(update.effective_user.id, symbol)
		except Exception as e:
			# Report error (as a Reply)
			self.logger.error(f'{update.effective_chat.full_name} ({update.effective_chat.id})\n{e}')
			update.message.reply_text(e.args[0], reply_to_message_id=update.message.message_id)
			return

		update.message.reply_text(f'Symbol {symbol} removed successfully')

	def favorites(self, update: Update, context: CallbackContext) -> None:
		try:
			favs = self.db.getFavorites(update.effective_user.id)
		except Exception as e:
			# Report error
			self.logger.error(f'{update.effective_chat.full_name} ({update.effective_chat.id})\n{e}')
			update.message.reply_text(e.args[0])

		keyboard = []
		for i,k in zip(favs[0::2], favs[1::2]):
			keyboard.append([
				InlineKeyboardButton(i[0], callback_data=i[0]),
				InlineKeyboardButton(k[0], callback_data=k[0])
			])
		if len(favs) % 2 == 1:
			keyboard.append([
				InlineKeyboardButton(favs[-1][0], callback_data=favs[-1][0])
			])

		replyMarkup = InlineKeyboardMarkup(keyboard)
		update.message.reply_text('Select stock', reply_markup=replyMarkup)

	def stockCallback(self, update: Update, context: CallbackContext) -> None:
		# CallbackQueries need to be answered, even if no notification to the user is needed
		# Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
		query = update.callback_query
		query.answer()

		# Getting symbol and scrapping the web
		try:
			message = self.scraper.getFromStock(query.data)
		except Exception as e:
			# Report error
			self.logger.error(f'{update.effective_chat.full_name} ({update.effective_chat.id})\n{e}')
			update.message.reply_text(e.args[0])
			return

		query.edit_message_text(f'Stock: {query.data.upper()}\n{message}')

	def __init__(self, logger: Logger):
		with open('token.txt', 'r') as f:
			token = f.readline().replace('\n', '')
		assert token is not None, 'Couldn\'t read the token'

		# Class vars
		self.logger = logger
		self.updater = Updater(token, use_context=True)

		# Project Modules
		self.db = Database()
		self.scraper = Scraper()
		self.utils = Utils()

		# Handlers
		dispatcher = self.updater.dispatcher
		dispatcher.add_handler(CommandHandler('start', 	self.start))
		dispatcher.add_handler(CommandHandler('help', 	self.helper))
		dispatcher.add_handler(CommandHandler('stock', 	self.stockCommand))
		dispatcher.add_handler(CommandHandler('addFav', self.addFavorite))
		dispatcher.add_handler(CommandHandler('removeFav', self.removeFavorite))
		dispatcher.add_handler(CommandHandler('favs', 	self.favorites))
		dispatcher.add_handler(CallbackQueryHandler(self.stockCallback))
