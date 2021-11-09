import json
from logging import Logger
from datetime import datetime, timedelta
from modules.updater import UpdaterService

from telegram.ext import CallbackContext

from modules.model.dates import *
from modules.database import DatabaseService

EASTERN = timezone('US/Eastern')
MADRID = timezone('Europe/Madrid')


class NotificationJobs:
    def on_open_market(self, context: CallbackContext) -> None:
        if datetime.now().isoweekday() in range(1, 6):
            job = context.job
            message = 'The market opens in 5 minutes'
            context.bot.send_message(job.context, text=message)

    def on_close_market(self, context: CallbackContext) -> None:
        if datetime.now().isoweekday() in range(1, 6):
            job = context.job
            message = 'The market closes in 5 minutes'
            context.bot.send_message(job.context, text=message)

    def __init__(self, logger: Logger, db_service: DatabaseService, updater_service: UpdaterService) -> None:
        self.logger = logger
        self.database = db_service
        self.updater = updater_service.updater

        with open('credentials.json', 'r') as file:
            data = json.load(file)

        for chat_id in data['alerts_whitelist']:
            open_time_message: datetime = datetime.combine(
                datetime.now(EASTERN), REGULAR_OPEN_MARKET).astimezone(MADRID) - timedelta(minutes=5)
            close_time_message: datetime = datetime.combine(
                datetime.now(EASTERN), REGULAR_CLOSE_MARKET).astimezone(MADRID) - timedelta(minutes=5)

            # Message about open market
            updater_service.updater.job_queue.run_daily(
                callback=self.on_open_market,
                time=open_time_message.time(),
                context=chat_id,
                name=f'open-{chat_id}')

            # Message about close market
            updater_service.updater.job_queue.run_daily(
                callback=self.on_close_market,
                time=close_time_message.time(),
                context=chat_id,
                name=f'close-{chat_id}')
