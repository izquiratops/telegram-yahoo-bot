import json
from typing import Generator, List
from logging import Logger
from datetime import datetime

from telegram.ext import CallbackContext

from modules.httpRequests import *
from modules.model.stock import Stock
from modules.model.alert import Alert
from modules.model.dates import *
from modules.database import DatabaseService
from modules.updater import UpdaterService


class AlertJobs:
    def _get_current_state(self, alert: Alert) -> bool:
        response = request_stocks(alert.symbol)
        current_price = Stock(response[0]).getLatestPrice()
        minRange = min(alert.reference_point, current_price)
        maxRange = max(alert.reference_point, current_price)

        return minRange < alert.target_point < maxRange

    def _iterate_alerts(self, alerts: List[Alert], chat_id: str) -> Generator[List[str], None, None]:
        for alert in alerts:
            triggered = self._get_current_state(alert)

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
            messages = list(self._iterate_alerts(alerts, chat_id))

            for message in messages:
                context.bot.send_message(job.context, text=message)

    def __init__(self, logger: Logger, db_service: DatabaseService, updater_service: UpdaterService) -> None:
        self.logger = logger
        self.database = db_service
        self.updater = updater_service.updater

        with open('info.json', 'r') as file:
            data = json.load(file)

        # Checking alerts every 5 minutes
        for chat_id in data['alerts_whitelist']:
            updater_service.updater.job_queue.run_repeating(
                callback=self.check,
                interval=60 * 5, # seconds * minutes
                context=chat_id,
                name=f'alerts-{chat_id}')
