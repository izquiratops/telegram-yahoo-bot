from urllib.request import urlopen
from bs4 import BeautifulSoup
from stock import Stock

class Scraper:
    def getFromStock(self, sym: str) -> Stock:
        targetPage = 'https://www.marketwatch.com/investing/stock/' + sym
        targetURL  = urlopen(targetPage)
        soup       = BeautifulSoup(targetURL, 'html.parser')

        try:
            parentElement         = soup.find('div', class_='intraday__data')
            intradayPrice         = parentElement.find('h3', class_='intraday__price')
            intradayChange        = parentElement.find('bg-quote', class_='intraday__change')
            intradayChangePoint   = intradayChange.find('span', class_='change--point--q')
            intradayChangePercent = intradayChange.find('span', class_='change--percent--q')
        except:
            return None

        priceValue   = intradayPrice.find('bg-quote').text
        pointValue   = intradayChangePoint.find('bg-quote').text
        percentValue = intradayChangePercent.find('bg-quote').text

        return Stock(priceValue, pointValue, percentValue)

    def __init__(self):
        pass
