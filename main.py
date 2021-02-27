#!/usr/bin/python3 -u

import logging
from telegram.ext import Updater
from logging.handlers import RotatingFileHandler

# Project modules
from methods import Commands, Callbacks

def main() -> None:
	# Logging
	logger = logging.getLogger('root')
	logger.setLevel(logging.INFO)
	logger.addHandler(setupLoggerHandler())

	# Init Dispatcher
	with open('token.txt', 'r') as f:
		token = f.readline().replace("\n", "")
		updater = Updater(token, use_context=True)

	# Setup Telegram Commands and Callbacks
	Commands(logger, updater.dispatcher)
	Callbacks(logger, updater.dispatcher)

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
	main()