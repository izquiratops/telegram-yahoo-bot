from math import floor
from urllib.request import urlopen
from bs4 import BeautifulSoup

class Stock:
	def __str__(self) -> str:
		return  f"{self.companyName} [{self.symbol.upper()}]" \
				f"\t{self.rockets}\n" \
				f"Price: {self.intradayPrice}$\n" \
				f"Change Point: {self.intradayChangePoint}$ " \
				f"({self.intradayChangePercent}%)\n"

	def __init__(self, symbol, companyName, intradayPrice, intradayChangePoint, intradayChangePercent):
		self.symbol: str 				= symbol
		self.companyName: str			= companyName
		self.intradayPrice: str			= intradayPrice
		self.intradayChangePoint: str	= intradayChangePoint
		self.intradayChangePercent: str	= intradayChangePercent
		self.rockets: str 				= '🚀' * floor(float(intradayChangePercent) / 5)

class Scraper:
	def getFromStock(self, symbol: str) -> str:
		targetPage = 'https://www.marketwatch.com/investing/stock/' + symbol
		try:
			targetURL = urlopen(targetPage, timeout=10)
		except:
			raise AssertionError('Couldn\'t reach the website')

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
		pass
