from logging import Logger
from modules.updater import UpdaterService

from modules.database import DatabaseService
from modules.updater import UpdaterService

from .handlers.bot import BotHandlers
from .handlers.messages import MessageHandlers
from .handlers.alerts import AlertHandlers
from .jobs.alerts import AlertJobs
from .jobs.notifications import NotificationJobs


class Bort:
    def __init__(self, logger: Logger, db_service: DatabaseService, updater_service: UpdaterService) -> None:
        BotHandlers(logger, db_service, updater_service)
        MessageHandlers(logger, db_service, updater_service)
        AlertHandlers(logger, db_service, updater_service)
        AlertJobs(logger, db_service, updater_service)
        NotificationJobs(logger, db_service, updater_service)
