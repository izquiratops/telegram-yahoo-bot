from datetime import datetime
from telegram.ext import CallbackContext

from modules.dates import *
from modules.stock import Stock
from modules.alerts import Alert
from .httpRequests import stock_symbols


def __check_alert(self, alert: Alert) -> bool:
    response = stock_symbols(alert.symbol)
    current_price = Stock(response[0]).getLatestPrice()
    minRange = min(alert.reference_point, current_price)
    maxRange = max(alert.reference_point, current_price)

    return minRange < alert.target_point < maxRange


def callback_alert(self, context: CallbackContext) -> None:
    job = context.job
    chat_id = job.name
    now = datetime.now()

    # Check weekday and market schedule
    if now.isoweekday() in range(1, 6) and EARLY_OPEN_MARKET < now.time() < LATE_CLOSE_MARKET:
        alerts: list[Alert] = self.alert_service.get_alerts(chat_id)

        for alert in alerts:
            triggered = self.__check_alert(alert)

            if triggered:
                # Once the alarm is triggered it's removed from db too
                self.alert_service.remove_alert(chat_id, alert)

                # Response
                message = f'{alert.symbol} has passed from {alert.target_point}!'
                context.bot.send_message(job.context, text=message)
