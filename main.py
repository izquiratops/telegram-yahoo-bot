import argparse
from urllib.request import urlopen
from bs4 import BeautifulSoup

parser = argparse.ArgumentParser(description='This thing get the current Premarket value from the input symbol')
parser.add_argument('--symbol', '-s', dest='symbol', required=True, help='Gimme a symbol')
args = parser.parse_args()

def getPremarket(sym: str):
	targetPage = 'https://www.marketwatch.com/investing/stock/' + sym
	targetURL = urlopen(targetPage)
	soup = BeautifulSoup(targetURL, 'html.parser')

	# Parent element:			div [class: parentElement]
	#
	# 1) Current Stock Price:	h3 [class: intraday__price]
	#
	# 2) The day range values can be found inside the 'intradayChange' element:
	# 							bg-quote [class: instraday__change]
	#
	# 2a) Point Value:			span [class: change--point--q] --> bg-quote
	# 2b) % Value:				span [class: change--percent--q] --> bg-quote

	parentElement = soup.find('div', class_='intraday__data')

	if parentElement is None:
		print(f'No values found for {sym}')

	intradayPrice = parentElement.find('h3', class_='intraday__price')
	intradayChange = parentElement.find('bg-quote', class_='intraday__change')
	intradayChangePoint = intradayChange.find('span', class_='change--point--q')
	intradayChangePercent = intradayChange.find('span', class_='change--percent--q')

	results = [intradayPrice, intradayChangePoint, intradayChangePercent]
	if None in results:
		print('something bad happened')

	for x in results:
		print(x.find('bg-quote').text)

if __name__ == '__main__':
	getPremarket(args.symbol)
