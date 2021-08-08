from typing import Generator

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CallbackContext, ConversationHandler

from modules.stock import Stock
from modules.alerts import Alert
from .httpRequests import stock_symbols


def __chunks(self, lst: list, n: int) -> Generator[list[str]]:
    # From lst to chunks of length n
    for i in range(0, len(lst), n):
        # Lambda function to map the content from Alert object into a string
        yield [f'{x}' for x in lst[i:i + n]]


def asking_add_alert(self, update: Update, _: CallbackContext) -> int:
    if self.alert_service.get_alerts() >= 20:
        update.message.reply_text(
            text='Limit reached 😢',
            parse_mode='HTML',
            reply_to_message_id=update.message.message_id)
        return ConversationHandler.END
    else:
        update.message.reply_text(
            text='Tell me which symbol and price.\nLike this <b>AAPL 250.50</b>',
            parse_mode='HTML',
            reply_to_message_id=update.message.message_id)
        return 0


def create_alert(self, update: Update, _: CallbackContext) -> int:
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
    response = stock_symbols(symbol)
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
    reply_keyboard = list(self.__chunks(alerts, 2))
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    update.message.reply_text(
        text='Which one?',
        reply_to_message_id=update.message.message_id,
        reply_markup=markup)
    return 0


def delete_alert(self, update: Update, _: CallbackContext) -> int:
    name = str(update.message.chat_id)

    try:
        # AAPL @250.0 --> Symbol: AAPL | Target: 250.0
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


def list_alerts(self, update: Update, _: CallbackContext) -> None:
    name = str(update.message.chat_id)
    message = ''

    alerts = self.alert_service.get_alerts(name)
    for alert in alerts:
        message += f'{alert.symbol.upper()}: {alert.target_point}\n'

    update.message.reply_text(message)
