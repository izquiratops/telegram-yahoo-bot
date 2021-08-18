import logging
from logging.handlers import RotatingFileHandler

from modules.bort import Bort
from modules.database import DatabaseService
from modules.updater import UpdaterService


def _setupLoggerHandler() -> RotatingFileHandler:
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
    logger = logging.getLogger('root')
    logger.setLevel(logging.INFO)
    logger.addHandler(_setupLoggerHandler())

    # Set up bot
    updater_service = UpdaterService()
    db_service = DatabaseService()
    Bort(logger, db_service, updater_service)

    # Run it
    updater_service.start()


if __name__ == '__main__':
    main()
