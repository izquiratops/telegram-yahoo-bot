import json
from typing import Tuple
from logging import Logger
from datetime import datetime, timedelta

from telegram.ext import (
    Updater,
    Filters,
    MessageHandler,
    CommandHandler,
    ConversationHandler
)

from modules.dates import *
from modules.alerts import AlertService

# Bort Moduleç
from .bot import start, helper
from .messages import stock
from .alerts import asking_add_alert, asking_delete_alert, create_alert, delete_alert, list_alerts
from .jobs.alerts import callback_alert
from .jobs.notifications import on_open_market, on_close_market


class Bort:
    def __readCredentials(self, filename: str) -> Tuple[str, str]:
        with open(filename, 'r') as file:
            data = json.load(file)

        return data['token'], data['alerts_whitelist']

    def __init__(self, logger: Logger) -> None:
        # ✨ Setup the logger from main and a shared Alert db service ✨
        self.logger = logger
        self.alert_service = AlertService()

        # ✨ Setup telegram credentials ✨
        token, whitelist = self.__readCredentials('info.json')
        updater = Updater(token, use_context=True)

        # ✨ Jobs ✨
        for chat_id in whitelist:
            open_time_message: datetime = datetime.combine(
                datetime.now(), CORE_OPEN_MARKET) - timedelta(minutes=5)
            close_time_message: datetime = datetime.combine(
                datetime.now(), CORE_CLOSE_MARKET) - timedelta(minutes=5)

            # Message about open market
            updater.job_queue.run_daily(
                callback=on_open_market,
                time=open_time_message.time(),
                context=chat_id,
                name=f'open-{chat_id}')

            # Message about close market
            updater.job_queue.run_daily(
                callback=on_close_market,
                time=close_time_message.time(),
                context=chat_id,
                name=f'close-{chat_id}')

            # Repeating job for checking Alerts every 5 minutes
            updater.job_queue.run_repeating(
                callback=callback_alert,
                interval=60 * 5,  # seconds * minutes
                context=chat_id,
                name=f'alerts-{chat_id}')

        # ✨ Handlers ✨
        # Common
        start_handler = CommandHandler('start', start)
        help_handler = CommandHandler('help', helper)

        # Text analyze
        message_handler = MessageHandler(Filters.text, stock)

        # Alerts
        # - List
        state_alerts_handler = CommandHandler(
            'list', list_alerts)

        # - Create
        entry_add_conversation = CommandHandler(
            'create', asking_add_alert)
        setting_add_conversation = MessageHandler(
            Filters.text, create_alert)

        create_alert_handler = ConversationHandler(
            entry_points=[entry_add_conversation],
            states={0: [setting_add_conversation]},
            fallbacks=[],
            conversation_timeout=60)

        # - Delete
        entry_delete_conversation = CommandHandler(
            'delete', asking_delete_alert)
        setting_delete_conversation = MessageHandler(
            Filters.text, delete_alert)

        delete_alert_handler = ConversationHandler(
            entry_points=[entry_delete_conversation],
            states={0: [setting_delete_conversation]},
            fallbacks=[],
            conversation_timeout=60)

        # ✨ Dispatcher setup ✨
        dispatcher = updater.dispatcher
        dispatcher.add_handler(start_handler)
        dispatcher.add_handler(help_handler)
        dispatcher.add_handler(state_alerts_handler)
        dispatcher.add_handler(create_alert_handler)
        dispatcher.add_handler(delete_alert_handler)
        dispatcher.add_handler(message_handler)
