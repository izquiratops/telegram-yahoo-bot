import logging, telegram
from datetime import datetime
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from modules.scraper import Scraper
from modules.utils import Utils

def start(update: Update, context: CallbackContext):
	context.bot.send_message(chat_id=update.effective_chat.id, text='Beep boop')

def help_command(update: Update, context: CallbackContext):
	message = '/stock *your symbol here*'
	context.bot.send_message(chat_id=update.effective_chat.id, text=message)

def stock(update: Update, context: CallbackContext):
	# Any comment older than 5 minutes ago will be ignored
	if utils.timeDiff(update.message.date) > 5:
		return

	# Getting symbol and scrapping the web
	symbol: str = update.message.text.split()[-1]
	message = scraper.getFromStock(symbol.lower())

	# Sending message
	logger.info(f'{update.effective_chat.full_name} - {message}')
	context.bot.send_message(
		chat_id=update.effective_chat.id, 
		text=message,
		reply_to_message_id=update.message.message_id)

def main() -> None:
	# Init Dispatcher
	f = open('token.txt', 'r')
	token = f.readline().replace("\n", "")
	updater = Updater(token, use_context=True)

	# Command Handlers
	start_handler = CommandHandler('start', start)
	help_handler = CommandHandler('help', help_command)
	stock_handler = CommandHandler('stock', stock)

	dispatcher = updater.dispatcher
	dispatcher.add_handler(start_handler)
	dispatcher.add_handler(help_handler)
	dispatcher.add_handler(stock_handler)

	# Start bot
	updater.start_polling()

if __name__ == '__main__':
	# Logging
	logging.basicConfig(
		filename='log.txt',
		filemode='a',
		level=logging.INFO,
		format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	logger = logging.getLogger()
	logger.setLevel(logging.INFO)

	# Init modules
	scraper = Scraper()
	utils = Utils()

	# Run bot
	main()