import random

from telegram import Update
from telegram.ext import CallbackContext

QUTOES = [
    '<i>You can’t beat the market but you can beat your meat</i>\n\n- Warren Buffet probably',
    '<i>¡Viva el vino de Ribeiro!</i>\n\n- Mariano Rajoy'
]


def start(self, update: Update, _: CallbackContext) -> None:
    update.message.reply_text(
        text=random.choice(QUTOES),
        parse_mode='HTML')


def helper(self, update: Update, _: CallbackContext) -> None:
    update.message.reply_text(
        text='<b>/start</b> - Greetings from Bort\n'
        '<b>/help</b> - You\'re currently here\n'
        '<b>... $<i>insert_symbol_here</i></b> ... - Ask for the price of a stock\n',
        parse_mode='HTML')
