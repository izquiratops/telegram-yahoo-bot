import os
from telegram.ext.updater import Updater


class TelegramBot:

    def start(self):
        # Start the Bot
        self.updater.start_polling()

        # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
        # SIGABRT. This should be used most of the time, since start_polling() is
        # non-blocking and will stop the bot gracefully.
        self.updater.idle()

    def __init__(self) -> None:
        token = os.environ.get('TELEGRAM_TOKEN')
        self.updater = Updater(token, use_context=True)
