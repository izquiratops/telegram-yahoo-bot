from typing import Generator

import json
from logging import Logger
from datetime import datetime

from telegram.ext import CallbackContext

from modules.dates import *
from modules.httpRequests import *
from modules.model.stock import Stock
from modules.model.alert import Alert
from modules.database import DatabaseService


class AlertJobs:
    def __get_current_state(self, alert: Alert) -> bool:
        response = request_stocks(alert.symbol)
        current_price = Stock(response[0]).getLatestPrice()
        minRange = min(alert.reference_point, current_price)
        maxRange = max(alert.reference_point, current_price)

        return minRange < alert.target_point < maxRange

    def __iterate_alerts(self, alerts: list[Alert], chat_id: str) -> Generator[list[str], None, None]:
        for alert in alerts:
            triggered = self.__get_current_state(alert)

            if triggered:
                # Once the alarm is triggered it's removed from db too
                DatabaseService.remove_alert(chat_id, alert)
                yield f'{alert.symbol} has passed from {alert.target_point}!'

    def check(self, context: CallbackContext) -> None:
        job = context.job
        chat_id = job.name
        now = datetime.now()

        # Check weekday and market schedule
        if now.isoweekday() in range(1, 6) and EARLY_OPEN_MARKET < now.time() < LATE_CLOSE_MARKET:
            alerts: list[Alert] = self.database.get_alerts(chat_id)
            messages = list(self.__iterate_alerts(alerts, chat_id))

            for message in messages:
                context.bot.send_message(job.context, text=message)

    def __init__(self, logger: Logger, database: DatabaseService) -> None:
        self.logger = logger
        self.database = database

        with open('info.json', 'r') as file:
            data = json.load(file)

        # Checking alerts every 5 minutes
        for chat_id in data['alerts_whitelist']:
            self.updater.job_queue.run_repeating(
                callback=self.__callback_alert,
                interval=60 * 5,  # seconds * minutes
                context=chat_id,
                name=f'alerts-{chat_id}')
