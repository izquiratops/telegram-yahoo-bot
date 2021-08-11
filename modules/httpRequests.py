import json
from urllib.request import urlopen


def request_stocks(symbols: list) -> list:
    # Yahoo accept one request with multiple stocks
    symbols = ','.join(symbols)
    BASEURL = "https://query1.finance.yahoo.com/v7/finance/quote?symbols="
    with urlopen(BASEURL + symbols, timeout=10) as response:
        read = response.read()
        read = json.loads(read)
    return read['quoteResponse']['result']


def request_cryptos(symbols: list) -> list:
    pass
