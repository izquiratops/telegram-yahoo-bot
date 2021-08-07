import re
import json
from datetime import datetime, time, timedelta
from pytz import timezone
from urllib.request import urlopen

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
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

MADRID = timezone('Europe/Madrid')
SETTING_VALUE = range(1)

# Early Trading Session: 7:00 a.m. to 9:30 a.m. ET
# Open 11:00 UTC (13:00 GMT+2)
EARLY_OPEN_MARKET = time(hour=11, minute=00, second=00, tzinfo=MADRID)
# Close 13:30 UTC (15:30 GMT+2)
EARLY_CLOSE_MARKET = time(hour=13, minute=30, second=00, tzinfo=MADRID)

# Core Trading Session: 9:30 a.m. to 4:00 p.m. ET
# Open 13:30 UTC (15:30 GMT+2)
CORE_OPEN_MARKET = time(hour=13, minute=30, second=00, tzinfo=MADRID)
# Close 20:00 UTC (22:00 GMT+2)
CORE_CLOSE_MARKET = time(hour=20, minute=00, second=00, tzinfo=MADRID)

# Late Trading Session: 4:00 p.m. to 8:00 p.m. ET
# Open 20:00 UTC (22:00 GMT+2)
LATE_OPEN_MARKET = time(hour=20, minute=00, second=00, tzinfo=MADRID)
# Close 00:00 UTC (02:00 GMT+2)
LATE_CLOSE_MARKET = time(hour=00, minute=00, second=00, tzinfo=MADRID)


class Bort:
    def timeDiff(self, input_time: datetime) -> int:
        date = input_time.replace(tzinfo=None)
        now = datetime.utcnow()
        return (now - date).total_seconds() / 60

    def chunks(self, lst, n):
        # From lst to chunks of length n
        for i in range(0, len(lst), n):
            # Lambda function to map the content from Alert object into a string
            yield [f'{x}' for x in lst[i:i + n]]

    def requestStockSymbols(self, symbols: list) -> list:
        # Yahoo accept one request with multiple stocks
        symbols = ','.join(symbols)

        BASEURL = "https://query1.finance.yahoo.com/v7/finance/quote?symbols="
        with urlopen(BASEURL + symbols, timeout=10) as response:
            read = response.read()
            read = json.loads(read)

        return read['quoteResponse']['result']

    def start(self, update: Update, _: CallbackContext) -> None:
        update.message.reply_text(
            text='<i>You can’t beat the market but you can beat your meat</i>\n\n'
            '- Warren Buffet probably',
            parse_mode='HTML')

    def helper(self, update: Update, _: CallbackContext) -> None:
        update.message.reply_text(
            text='<b>/start</b> - Greetings from Bort\n'
            '<b>/help</b> - You\'re currently here\n'
            '<b>... $<i>insert_symbol_here</i></b> ... - Ask for the price of a stock\n',
            parse_mode='HTML')

    def stock(self, update: Update, _: CallbackContext) -> None:
        # Ignore message edits OR requests older than 5 mins
        if not update.message or self.timeDiff(update.message.date) > 5:
            return

        # Ignore message if has no symbols on it
        symbols = re.findall('[$|&][^\\s]*', update.message.text)
        if len(symbols) == 0:
            return

        # List of unique symbols
        unique_symbols = list(dict.fromkeys(symbols))
        # Split into list of stocks and cryptos (get rid of $|& in the process)
        unique_stocks = [x[1:] for x in unique_symbols if x[0] == '$']
        # unique_cryptos = [x[1:] for x in unique_symbols if x[0] == '&']

        # Yahoo Finance Request
        response = self.requestStockSymbols(unique_stocks)

        # Get User for log porposes
        user = update.message.from_user

        if not response:
            self.logger.error(
                f'{user.full_name} '
                f'[{update.message.from_user.id}]: '
                f'{unique_stocks}')
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
                disable_web_page_preview=True,
                reply_to_message_id=update.message.message_id)

    def callback_alert(self, context: CallbackContext) -> None:
        now = datetime.now()

        # Check weekday and market schedule
        if (now.isoweekday() in range(1, 6)) and EARLY_OPEN_MARKET < now.time() < LATE_CLOSE_MARKET:
            job = context.job
            chat_id: int = job.name
            alerts = self.alert_service.get_alerts(chat_id)

            for alert in alerts:
                # Check every alarm for this chat
                response = self.requestStockSymbols(alert.symbol)
                current_price = Stock(response[0]).getLatestPrice()

                minRange = min(alert.reference_point, current_price)
                maxRange = max(alert.reference_point, current_price)
                if minRange < alert.target_point < maxRange:
                    # Once the alarm is triggered it's removed from db too
                    self.alert_service.remove_alert(chat_id, alert)

                    # Response
                    message = f'{alert.symbol} has passed from {alert.target_point}!'
                    context.bot.send_message(job.context, text=message)

    def open_market_reply(self, context: CallbackContext) -> None:
        if (datetime.now().isoweekday() in range(1, 6)):
            job = context.job
            message = 'El mercado abre en 5 minutos'
            context.bot.send_message(job.context, text=message)

    def close_market_reply(self, context: CallbackContext) -> None:
        if (datetime.now().isoweekday() in range(1, 6)):
            job = context.job
            message = 'El mercado cierra en 5 minutos'
            context.bot.send_message(job.context, text=message)

    def state_alerts(self, update: Update, _: CallbackContext) -> None:
        name = str(update.message.chat_id)
        message: str = ''

        alerts = self.alert_service.get_alerts(name)
        for alert in alerts:
            message += f'{alert.symbol.upper()}: {alert.target_point}\n'

        update.message.reply_text(message)

    def asking_add_alert(self, update: Update, _: CallbackContext) -> int:
        if self.alert_service.get_alerts() >= 20:
            update.message.reply_text(
                text='Limit of 20 alerts reached 😢',
                parse_mode='HTML',
                reply_to_message_id=update.message.message_id)
            return ConversationHandler.END
        else:
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
        response = self.requestStockSymbols(symbol)
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
                chat_id=name,
                symbol=symbol.lower(),
                target_point=float(target_point))
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
        # 'data' holds the bot token and whitelisted groups for alert jobs
        with open('info.json', 'r') as file:
            data = json.load(file)

        self.logger = logger
        self.updater = Updater(data['token'], use_context=True)
        self.alert_service = AlertService()

        # ✨ Alert jobs ✨
        for chat_id in data['alerts_whitelist']:
            open_time: datetime = datetime.combine(
                datetime.now(), CORE_OPEN_MARKET) - timedelta(minutes=5)
            close_time: datetime = datetime.combine(
                datetime.now(), CORE_CLOSE_MARKET) - timedelta(minutes=5)

            self.updater.job_queue.run_daily(
                callback=self.open_market_reply,
                time=open_time.time(),
                context=chat_id,
                name=f'open-{chat_id}')
            self.updater.job_queue.run_daily(
                callback=self.close_market_reply,
                time=close_time.time(),
                context=chat_id,
                name=f'close-{chat_id}')
            self.updater.job_queue.run_repeating(
                callback=self.callback_alert,
                interval=60 * 1,  # seconds * minutes
                context=chat_id,
                name=f'alerts-{chat_id}')

        # ✨ Handlers ✨
        # ❗ Common
        start_handler = CommandHandler('start', self.start)
        help_handler = CommandHandler('help', self.helper)
        # ❗ Alerts
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
        # ❗ Create alert conversation
        create_alert_handler = ConversationHandler(
            entry_points=[asking_add_alert_handler],
            states={SETTING_VALUE: [setting_add_alert_handler]},
            fallbacks=[],
            conversation_timeout=60)
        # ❗ Delete alert conversation
        delete_alert_handler = ConversationHandler(
            entry_points=[asking_delete_alert_handler],
            states={SETTING_VALUE: [setting_delete_alert_handler]},
            fallbacks=[],
            conversation_timeout=60)
        # ❗ Handler for getting symbols
        message_handler = MessageHandler(Filters.text, self.stock)

        # ✨ Dispatcher setup ✨
        dispatcher = self.updater.dispatcher
        dispatcher.add_handler(start_handler)
        dispatcher.add_handler(help_handler)
        dispatcher.add_handler(state_alerts_handler)
        dispatcher.add_handler(create_alert_handler)
        dispatcher.add_handler(delete_alert_handler)
        dispatcher.add_handler(message_handler)
