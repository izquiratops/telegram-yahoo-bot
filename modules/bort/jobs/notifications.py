import json
from logging import Logger
from datetime import datetime, timedelta

from telegram.ext import CallbackContext

from modules.dates import *
from modules.database import DatabaseService


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

    def __init__(self, logger: Logger, database: DatabaseService) -> None:
        self.logger = logger
        self.database = database

        with open('info.json', 'r') as file:
            data = json.load(file)

        for chat_id in data['alerts_whitelist']:
            open_time_message: datetime = datetime.combine(
                datetime.now(), CORE_OPEN_MARKET) - timedelta(minutes=5)
            close_time_message: datetime = datetime.combine(
                datetime.now(), CORE_CLOSE_MARKET) - timedelta(minutes=5)

            # Message about open market
            self.updater.job_queue.run_daily(
                callback=self.__on_open_market,
                time=open_time_message.time(),
                context=chat_id,
                name=f'open-{chat_id}')

            # Message about close market
            self.updater.job_queue.run_daily(
                callback=self.__on_close_market,
                time=close_time_message.time(),
                context=chat_id,
                name=f'close-{chat_id}')
