import logging, telegram
from telegram.ext import Updater, CommandHandler
from modules.scraper import Scraper

def start(update, context):
	context.bot.send_message(chat_id=update.effective_chat.id, text='Beep boop')

def help_command(update, context):
	message = '/stock *your symbol here*'
	context.bot.send_message(chat_id=update.effective_chat.id, text=message)

def stock(update, context):
	symbol: str = update.message.text.split()[-1]
	logger.info(symbol)
	result = scraper.getFromStock(symbol.lower())

	if result is not None:
		message = f'{result}'
	else:
		message = 'Timeout or wrong symbol'

	logger.info(f'{update.effective_chat.full_name} - {message}')
	context.bot.send_message(chat_id=update.effective_chat.id, text=message)

if __name__ == '__main__':
	# Get Token
	f = open('token.txt', 'r')
	token = f.readline().replace("\n", "")
	f.close()

	# Command Handlers	
	start_handler = CommandHandler('start', start)
	help_handler = CommandHandler('help', help_command)
	stock_handler = CommandHandler('stock', stock)

	# Init Dispatcher
	updater = Updater(token, use_context=True)
	dispatcher = updater.dispatcher
	dispatcher.add_handler(start_handler)
	dispatcher.add_handler(help_handler)
	dispatcher.add_handler(stock_handler)

	# Init Scraper
	scraper = Scraper()

	# Logging
	logging.basicConfig(
		filename='log.txt',
		filemode='a',
		level=logging.INFO,
		format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	logger = logging.getLogger()
	logger.setLevel(logging.INFO)

	# Start bot
	updater.start_polling()
