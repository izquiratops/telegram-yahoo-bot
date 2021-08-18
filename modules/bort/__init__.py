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
        # Commands
        BotHandlers(logger, db_service, updater_service)
        AlertHandlers(logger, db_service, updater_service)
        # Check commands first, then message regex
        MessageHandlers(logger, db_service, updater_service)
        # Alerts
        AlertJobs(logger, db_service, updater_service)
        NotificationJobs(logger, db_service, updater_service)

