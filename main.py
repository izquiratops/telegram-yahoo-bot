import logging
import json
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


def _readToken(path: str = 'info.json') -> str:
    with open(path, 'r') as file:
        data = json.load(file)

    return data['token']


def main() -> None:
    logger = logging.getLogger('root')
    logger.setLevel(logging.INFO)
    logger.addHandler(_setupLoggerHandler())

    token = _readToken()
    updater_service = UpdaterService(token)
    db_service = DatabaseService()

    # Setup bot
    Bort(logger, db_service, updater_service)

    # Run it
    updater_service.start()


if __name__ == '__main__':
    main()
