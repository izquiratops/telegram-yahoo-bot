import json
from logging import Logger
from datetime import datetime, timedelta
from pytz import timezone, UTC

from telegram.ext import CallbackContext

from modules.model.dates import *
from modules.database import DatabaseService
from modules.updater import UpdaterService

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
            open_time_time = datetime.combine(
                datetime.now(), REGULAR_OPEN_MARKET)
            close_time_time = datetime.combine(
                datetime.now(), REGULAR_CLOSE_MARKET)

            open_time_ET = EASTERN.localize(
                open_time_time)
            close_time_ET = EASTERN.localize(
                close_time_time)

            open_datetime = open_time_ET.astimezone(
                UTC) - timedelta(minutes=5)
            close_datetime = close_time_ET.astimezone(
                UTC) - timedelta(minutes=5)

            updater_service.updater.job_queue.run_daily(
                callback=self.on_open_market,
                time=open_datetime.time(),
                context=chat_id,
                name=f'open-{chat_id}')
            updater_service.updater.job_queue.run_daily(
                callback=self.on_close_market,
                time=close_datetime.time(),
                context=chat_id,
                name=f'close-{chat_id}')
