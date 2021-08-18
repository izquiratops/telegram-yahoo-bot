import json
from telegram.ext.updater import Updater


class UpdaterService():

    def start(self):
        # Start the Bot
        self.updater.start_polling()

        # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
        # SIGABRT. This should be used most of the time, since start_polling() is
        # non-blocking and will stop the bot gracefully.
        self.updater.idle()

    def __init__(self) -> None:
        print('Updater init')
        with open('./info.json', 'r') as file:
            data = json.load(file)

        self.updater = Updater(data['token'], use_context=True)
