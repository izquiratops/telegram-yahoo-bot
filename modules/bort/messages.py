import re
from datetime import datetime
from telegram import Update
from telegram.ext import CallbackContext

from modules.stock import Stock
from .httpRequests import stock_symbols


def __minutes_difference(self, input_time: datetime) -> int:
    date = input_time.replace(tzinfo=None)
    now = datetime.utcnow()
    return (now - date).total_seconds() / 60


def stock(self, update: Update, _: CallbackContext) -> None:
    # Ignore message edits OR requests older than 5 mins
    if not update.message or self.__minutes_difference(update.message.date) > 5:
        return

    # Ignore message if has no symbols on it
    symbols = re.findall('[$|&][^\\s]*', update.message.text)
    if len(symbols) == 0:
        return

    # List of unique symbols
    unique_symbols = list(dict.fromkeys(symbols))

    # Split into list of stocks and cryptos (get rid of $|& in the process)
    unique_stocks = [x[1:] for x in unique_symbols if x[0] == '$']
    unique_cryptos = [x[1:] for x in unique_symbols if x[0] == '&']

    # Yahoo Finance Request
    response = stock_symbols(unique_stocks)

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

    # Reply
    if (response_text != ''):
        update.message.reply_text(
            text=response_text,
            parse_mode='HTML',
            disable_web_page_preview=True,
            reply_to_message_id=update.message.message_id)
