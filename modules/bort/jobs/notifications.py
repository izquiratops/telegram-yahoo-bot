from datetime import datetime
from telegram.ext import CallbackContext


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
