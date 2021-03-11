import logging
from logging.handlers import RotatingFileHandler
from modules.bort import Bort

def setupLoggerHandler() -> RotatingFileHandler:
	logFormatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
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

def main() -> None:
	# Logging
	logger = logging.getLogger('root')
	logger.setLevel(logging.INFO)
	logger.addHandler(setupLoggerHandler())

	# Setup Telegram Bot logic
	bort = Bort(logger)

	# Start bot
	bort.updater.start_polling()
	bort.updater.idle()

if __name__ == '__main__':
	main()