import logging
from logging.handlers import RotatingFileHandler
from modules.bort import Bort


def setupLoggerHandler() -> RotatingFileHandler:
    logFormatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s')
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

    # Start the Bot
    bort.updater.start_polling()

    # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
    # SIGABRT. This should be used most of the time, since start_polling() is
    # non-blocking and will stop the bot gracefully.
    bort.updater.idle()


if __name__ == '__main__':
    main()
