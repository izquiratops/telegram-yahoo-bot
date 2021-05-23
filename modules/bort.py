import re
import json
from datetime import datetime
from urllib.request import urlopen
from collections import deque

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply
from telegram.ext import (
    Updater,
    Filters,
    CallbackContext,
    MessageHandler,
    CommandHandler,
    ConversationHandler
)

from modules.stock import Stock
from modules.alerts import AlertService, Alert

from logging import Logger

SETTING_VALUE = range(1)


class Bort:
    '''A module-level docstring

    Notice the comment above the docstring specifying the encoding.
    Docstrings do appear in the bytecode, so you can access this through
    the ``__doc__`` attribute. This is also what you'll see if you call
    help() on a module or any other Python object.
    '''

    def timeDiff(self, input_time: datetime) -> int:
        date = input_time.replace(tzinfo=None)
        now = datetime.utcnow()
        return (now - date).total_seconds() / 60

    def chunks(self, lst, n):
        # From lst to chunks of length n
        for i in range(0, len(lst), n):
            # Lambda function to map the content from Alert object into a string
            yield [f'{x}' for x in lst[i:i + n]]

    def requestSymbols(self, symbols: str) -> list:
        BASEURL = "https://query1.finance.yahoo.com/v7/finance/quote?symbols="
        with urlopen(BASEURL + symbols, timeout=10) as response:
            read = response.read()
            read = json.loads(read)

        return read['quoteResponse']['result']

    def start(self, update: Update, context: CallbackContext) -> None:
        update.message.reply_text(
            text='<i>You can’t beat the market but you can beat your meat</i>\n\n'
            '- Warren Buffet probably',
            parse_mode='HTML')

    def helper(self, update: Update, context: CallbackContext) -> None:
        update.message.reply_text(
            text='<b>/start</b> - Greetings from Bort\n'
            '<b>/help</b> - You\'re currently here\n'
            '<b>... $<i>insert_symbol_here</i></b> ... - Ask for the price of a stock\n',
            parse_mode='HTML')

    def tail(self, update: Update, context: CallbackContext) -> None:
        with open('log.txt') as file:
            tail = deque(file, 10)
        for line in tail:
            update.message.reply_text(line)

    def stock(self, update: Update, context: CallbackContext) -> None:
        # Ignore message edits OR requests older than 5 mins
        if not update.message or self.timeDiff(update.message.date) > 5:
            return

        # Ignore message if has no symbols on it
        symbols = re.findall('[$][^\\s]*', update.message.text)
        if len(symbols) == 0:
            return

        # Get User for log porposes
        user = update.message.from_user
        # List of unique symbols
        unique_symbols = list(dict.fromkeys(symbols))
        # Get rid of $
        unique_symbols = [x[1:] for x in unique_symbols]
        unique_symbols = ','.join(unique_symbols)

        # Yahoo Finance Request
        response = self.requestSymbols(unique_symbols)
        if not response:
            self.logger.error(
                f'{user.full_name} '
                f'[{update.message.from_user.id}]: '
                f'{unique_symbols}')
            return

        # Write Response
        response_text: str = ''
        for element in response:
            stock = Stock(element)
            response_text += f'{stock}\n'
            self.logger.info(
                f'{user.full_name} '
                f'[{update.message.from_user.id}]: '
                f'{stock.symbol}')

        # Reply!
        if (response_text != ''):
            update.message.reply_text(
                text=response_text,
                parse_mode='HTML',
                reply_to_message_id=update.message.message_id)

    def callback_alert(self, context: CallbackContext) -> None:
        job = context.job
        chat_id: int = job.name
        alerts = self.alert_service.get_alerts(chat_id)

        for alert in alerts:
            # Check every alarm for this chat
            response = self.requestSymbols(alert.symbol)
            current_price = Stock(response[0]).getLatestPrice()

            minRange = min(alert.reference_point, current_price)
            maxRange = max(alert.reference_point, current_price)
            if minRange < alert.target_point < maxRange:
                # Once the alarm is triggered it's removed from db too
                self.alert_service.remove_alert(chat_id, alert)

                # Response
                message = f'{alert.symbol} has passed from {alert.target_point}!'
                # f'Current price: {current_price}'
                context.bot.send_message(job.context, text=message)

    def enable_alerts(self, update: Update, context: CallbackContext) -> None:
        update.message.reply_text('Notifications activated 🎉🥳')

        chat_id: int = update.message.chat_id
        context.job_queue.run_repeating(callback=self.callback_alert,
                                        interval=60 * 10,
                                        context=chat_id,
                                        name=str(chat_id))

    def disable_alerts(self, update: Update, context: CallbackContext) -> None:
        update.message.reply_text('Any alert won\'t be notified anymore 🤫')

        name = str(update.message.chat_id)
        current_jobs = context.job_queue.get_jobs_by_name(name)
        for current_job in current_jobs:
            current_job.schedule_removal()

    def state_alerts(self, update: Update, context: CallbackContext) -> None:
        name = str(update.message.chat_id)
        current_jobs = context.job_queue.get_jobs_by_name(name)

        message: str = ''
        if current_jobs:
            message += 'Currently active\n\n'
        else:
            message += 'Not active\n\n'

        alerts = self.alert_service.get_alerts(name)
        for alert in alerts:
            message += f'{alert.symbol.upper()}: {alert.target_point}\n'

        update.message.reply_text(message)

    def asking_add_alert(self, update: Update, _: CallbackContext) -> int:
        update.message.reply_text(
            text='Tell me which symbol and price.\nLike this <b>AAPL 250.50</b>',
            parse_mode='HTML',
            reply_to_message_id=update.message.message_id)

        return SETTING_VALUE

    def creating_alert(self, update: Update, _: CallbackContext) -> int:
        name = str(update.message.chat_id)

        # Messages must follow the pattern SYMBOL *space* PRICE
        try:
            symbol, target = update.message.text.split(' ')
        except:
            update.message.reply_text(
                text='Bad syntax',
                reply_to_message_id=update.message.message_id)
            return ConversationHandler.END

        # Current price of the stock needed
        response = self.requestSymbols(symbol)
        if not response:
            update.message.reply_text(
                text='Symbol not found',
                reply_to_message_id=update.message.message_id)
            return ConversationHandler.END

        # Save the new Alert into the database
        try:
            data = {
                # Saved always as lowercase
                'symbol': symbol.lower(),
                'reference_point': Stock(response[0]).getLatestPrice(),
                'target_point': float(target)
                # Testing value
                # 'reference_point': 1.00,
            }
            self.alert_service.create_alert(name, Alert(data))
        except:
            update.message.reply_text(
                text='<i>Oh oh made an oopsie</i>',
                parse_mode='HTML',
                reply_to_message_id=update.message.message_id)
            return ConversationHandler.END

        # Response
        update.message.reply_text(
            text='Done! 🎉',
            reply_to_message_id=update.message.message_id)
        return ConversationHandler.END

    def asking_delete_alert(self, update: Update, _: CallbackContext) -> int:
        name = str(update.message.chat_id)
        # Get current alerts for this chat
        alerts = self.alert_service.get_alerts(name)
        # Add 'Cancel' option
        alerts.append('Nevermind 🤔')
        # Setup keyboard markup
        reply_keyboard = list(self.chunks(alerts, 2))

        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        update.message.reply_text(
            text='Which one?',
            reply_to_message_id=update.message.message_id,
            reply_markup=markup)
        return SETTING_VALUE

    def deleting_alert(self, update: Update, _: CallbackContext) -> int:
        name = str(update.message.chat_id)

        # AAPL @250.0 --> Symbol: AAPL | Target: 250.0
        try:
            symbol, target_point = update.message.text.split(' ')
        except:
            update.message.reply_text(
            text='🥺',
            reply_to_message_id=update.message.message_id,
            reply_markup=ReplyKeyboardRemove())
            return ConversationHandler.END

        try:
            # Search for the selected Alert
            result = self.alert_service.search_markup_response(
                chat_id = name, 
                symbol = symbol.lower(),
                target_point = float(target_point))
            # Remove from db
            self.alert_service.remove_alert(name, result)
            # Reply
            update.message.reply_text(
                text='Done! 🎉',
                reply_to_message_id=update.message.message_id,
                reply_markup=ReplyKeyboardRemove())
        except:
            update.message.reply_text(
                text='I couldn\'t remove it',
                reply_to_message_id=update.message.message_id,
                reply_markup=ReplyKeyboardRemove())

        return ConversationHandler.END

    def __init__(self, logger: Logger):
        with open('token.txt', 'r') as file:
            token = file.readline().replace('\n', '')

        # Class vars
        self.logger = logger
        self.updater = Updater(token, use_context=True)

        # Alert class to get access into the db
        self.alert_service = AlertService()

        # Setup dispatcher
        dispatcher = self.updater.dispatcher

        # Common handlers
        start_handler = CommandHandler('start', self.start)
        help_handler = CommandHandler('help', self.helper)
        command_handler = CommandHandler('tail', self.tail)

        # Alert handlers
        enable_alerts_handler = CommandHandler(
            'enable', self.enable_alerts)
        remove_alerts_handler = CommandHandler(
            'disable', self.disable_alerts)
        state_alerts_handler = CommandHandler(
            'list', self.state_alerts)
        asking_add_alert_handler = CommandHandler(
            'create', self.asking_add_alert)
        setting_add_alert_handler = MessageHandler(
            Filters.text, self.creating_alert)
        asking_delete_alert_handler = CommandHandler(
            'delete', self.asking_delete_alert)
        setting_delete_alert_handler = MessageHandler(
            Filters.text, self.deleting_alert)

        # Create Alert conversation
        create_alert_handler = ConversationHandler(
            entry_points=[asking_add_alert_handler],
            states={SETTING_VALUE: [setting_add_alert_handler]},
            fallbacks=[],
            conversation_timeout=60)

        # Delete Alert conversation
        delete_alert_handler = ConversationHandler(
            entry_points=[asking_delete_alert_handler],
            states={SETTING_VALUE: [setting_delete_alert_handler]},
            fallbacks=[],
            conversation_timeout=60)

        # Handler for getting stocks on messages
        message_handler = MessageHandler(Filters.text, self.stock)

        dispatcher.add_handler(start_handler)
        dispatcher.add_handler(help_handler)
        dispatcher.add_handler(command_handler)
        dispatcher.add_handler(enable_alerts_handler)
        dispatcher.add_handler(remove_alerts_handler)
        dispatcher.add_handler(state_alerts_handler)
        dispatcher.add_handler(create_alert_handler)
        dispatcher.add_handler(delete_alert_handler)
        dispatcher.add_handler(message_handler)
