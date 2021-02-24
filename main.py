import logging, telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from scraper import Scraper

def start(update, context):
	context.bot.send_message(chat_id=update.effective_chat.id, text="Beep boop, soy izqui pero la vacuna contra el covid me ha convertido en un robot")

def echo(update, context):
	symbol = update.message.text
	result = scraper.getFromStock(symbol)

	if result is not None:
		message = result.intradayPrice + ' (' + result.intradayChangePoint + ', ' + result.intradayChangePercent + ')'
	else:
		message = 'Couldn\'t find the symbol'

	logger.info(str(update.effective_chat.full_name) + ' - ' + message)
	context.bot.send_message(chat_id=update.effective_chat.id, text=message)

if __name__ == '__main__':
	# Get Token
	with open('token.txt', 'r') as f:
		token = f.readline()

	# Command Handlers	
	start_handler = CommandHandler('start', start)
	echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)

	# Init Dispatcher
	updater = Updater(token, use_context=True)
	dispatcher = updater.dispatcher
	dispatcher.add_handler(start_handler)
	dispatcher.add_handler(echo_handler)

	# Init Scraper
	scraper = Scraper()

	# Logging
	logging.basicConfig(level=logging.DEBUG,
					format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	logger = logging.getLogger()
	logger.setLevel(logging.INFO)

	# Start bot
	updater.start_polling()
