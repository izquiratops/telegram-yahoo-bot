#!/usr/bin/python3 -u

import logging, telegram
from logging.handlers import RotatingFileHandler
from datetime import datetime
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from modules.scraper import Scraper
from modules.utils import Utils

def start(update: Update, context: CallbackContext) -> None:
	context.bot.send_message(chat_id=update.effective_chat.id, text='Beep boop')

def help_command(update: Update, context: CallbackContext) -> None:
	message = '/stock *your symbol here*'
	context.bot.send_message(chat_id=update.effective_chat.id, text=message)

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
	context.bot.send_message(
		chat_id=update.effective_chat.id, 
		text=message,
		reply_to_message_id=update.message.message_id)

def main() -> None:
	# Init Dispatcher
	f = open('token.txt', 'r')
	token = f.readline().replace("\n", "")
	updater = Updater(token, use_context=True)

	# Command Handlers
	dispatcher = updater.dispatcher

	# Start
	start_handler = CommandHandler('start', start)
	dispatcher.add_handler(start_handler)
	# Help
	help_handler = CommandHandler('help', help_command)
	dispatcher.add_handler(help_handler)
	# Stock
	stock_handler = CommandHandler('stock', stock)
	dispatcher.add_handler(stock_handler)

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