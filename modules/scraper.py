from math import floor
from urllib.request import urlopen
from bs4 import BeautifulSoup

BASEURL = 'https://www.marketwatch.com/investing/'

class Scraper:
	"""
	Marketwatch web scraper.
	"""

	def legacyGetStock(self, symbol: str) -> str:
		# Retrieve symbol from cache
		try:
			kind = self.cache[symbol]
			targetURL = urlopen(BASEURL + kind + symbol, timeout=5)

		# Not found block
		except:
			# Looking for Stocks, then Funds
			for kind in ['stock/', 'fund/']:
				try:
					targetURL = urlopen(BASEURL + kind + symbol, timeout=5)
					self.cache[symbol] = kind
					break
				except:
					continue

			assert targetURL is not None, "Couldn't reach the website"

		soup = BeautifulSoup(targetURL, 'html.parser')
		try:
			companyName				= soup.find('h1', class_='company__name')
			parentElement			= soup.find('div', class_='intraday__data')
			intradayPrice			= parentElement.find('h3', class_='intraday__price')
			intradayChange			= parentElement.find('bg-quote', class_='intraday__change')
			intradayChangePoint		= intradayChange.find('span', class_='change--point--q')
			intradayChangePercent	= intradayChange.find('span', class_='change--percent--q')
		except:
			raise AssertionError('Couldn\'t find the symbol')

		nameValue		= companyName.text
		priceValue		= intradayPrice.find('bg-quote').text
		pointValue		= intradayChangePoint.find('bg-quote').text
		percentValue	= intradayChangePercent.find('bg-quote').text[:-1]

		stock = Stock(symbol, nameValue, priceValue, pointValue, percentValue)
		return f'{stock}'

	def __init__(self):
		self.cache = dict()
		pass
