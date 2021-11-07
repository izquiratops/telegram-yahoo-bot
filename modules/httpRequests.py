import json
from urllib.request import urlopen
from urllib.error import URLError, HTTPError


def request_stocks(symbols: list) -> list:
    # Yahoo accept one request with multiple stocks
    symbols = ','.join(symbols)
    BASEURL = "https://query1.finance.yahoo.com/v7/finance/quote?symbols="
    try:
        with urlopen(BASEURL + symbols, timeout=10) as response:
            read = response.read()
            read = json.loads(read)
    except (URLError, HTTPError) as error:
        raise ConnectionError(error)

    return read['quoteResponse']['result']
