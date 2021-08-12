import json
from logging import Logger

from telegram.ext import Updater

from modules.dates import *
from modules.database import DatabaseService

from .handlers.bot import BotHandlers
from .handlers.messages import MessageHandlers
from .handlers.alerts import AlertHandlers
from .jobs.alerts import AlertJobs
from .jobs.notifications import NotificationJobs


class Bort:
    def __init__(self, logger: Logger, db_service: DatabaseService) -> None:
        self.logger = logger
        self.database_service = db_service

        with open('info.json', 'r') as file:
            data = json.load(file)

        updater = Updater(data['token'], use_context=True)

        BotHandlers(logger, db_service, updater)
        MessageHandlers(logger, db_service, updater)
        AlertHandlers(logger, db_service, updater)

        AlertJobs(logger, db_service, updater)
        NotificationJobs(logger, db_service, updater)

        # Start the Bot
        updater.start_polling()

        # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
        # SIGABRT. This should be used most of the time, since start_polling() is
        # non-blocking and will stop the bot gracefully.
        updater.idle()
