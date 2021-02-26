#!/usr/bin/python3 -u

import logging, telegram
from logging.handlers import RotatingFileHandler
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler
from modules.scraper import Scraper
from modules.utils import Utils

def start(update: Update, context: CallbackContext) -> None:
	update.message.reply_text('Beep boop')

def helpCommand(update: Update, context: CallbackContext) -> None:
	update.message.reply_text('/stock *your symbol here*')

def stock(update: Update, context: CallbackContext) -> None:
	# Any comment older than 5 minutes ago will be ignored
	if utils.timeDiff(update.message.date) > 5:
		return

	# Getting symbol and scrapping the web
	request = update.message.text.split()
	if len(request) != 2:
		return
	else:
		message = scraper.getFromStock(request[1].replace('$','').lower())

	# Sending message
	logger.info(f'{update.effective_chat.full_name} ({update.effective_chat.id}) -> {request}')
	update.message.reply_text(message, reply_to_message_id=update.message.message_id)

def favorites(update: Update, context: CallbackContext) -> None:
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

def stockCallback(update: Update, context: CallbackContext) -> None:
	# CallbackQueries need to be answered, even if no notification to the user is needed
	# Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
	query = update.callback_query
	query.answer()

	# Getting symbol and scrapping the web
	message = scraper.getFromStock(query.data)
	query.edit_message_text(f'Stock: {query.data.upper()}\n{message}')

def main() -> None:
	# Init Dispatcher
	f = open('token.txt', 'r')
	token = f.readline().replace("\n", "")
	updater = Updater(token, use_context=True)

	# Command Handlers
	dispatcher = updater.dispatcher

	# Start
	startHandler = CommandHandler('start', start)
	dispatcher.add_handler(startHandler)
	# Help
	helpHandler = CommandHandler('help', helpCommand)
	dispatcher.add_handler(helpHandler)
	# Stock
	stockHandler = CommandHandler('stock', stock)
	dispatcher.add_handler(stockHandler)
	# Favs
	favsHandler = CommandHandler('favs', favorites)
	dispatcher.add_handler(favsHandler)
	# Fav. Stock Callback
	dispatcher.add_handler(CallbackQueryHandler(stockCallback))

	# Start bot
	updater.start_polling()
	updater.idle()

def setupLoggerHandler() -> RotatingFileHandler:
	# https://stackoverflow.com/questions/24505145/how-to-limit-log-file-size-in-python
	logFormatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	logFile = 'log.txt'

	logHandler = RotatingFileHandler(logFile,
		mode='a',
		maxBytes=5*1024*1024,
		backupCount=2,
		encoding=None,
		delay=0)
	logHandler.setFormatter(logFormatter)
	logHandler.setLevel(logging.INFO)

	return logHandler

if __name__ == '__main__':
	# Logging
	logger = logging.getLogger('root')
	logger.setLevel(logging.INFO)
	logger.addHandler(setupLoggerHandler())

	# Init modules
	scraper = Scraper()
	utils = Utils()

	# Run bot
	main()