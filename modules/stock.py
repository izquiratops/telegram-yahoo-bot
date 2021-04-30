from math import floor
from dataclasses import dataclass


@dataclass
class Stock:
    '''A module-level docstring

    Notice the comment above the docstring specifying the encoding.
    Docstrings do appear in the bytecode, so you can access this through
    the ``__doc__`` attribute. This is also what you'll see if you call
    help() on a module or any other Python object.
    '''

    symbol: str
    displayName: str
    totalChangePercent: float

    regularMarketPrice: float
    regularMarketChange: float
    regularMarketChangePercent: float

    postMarketPrice: float
    postMarketChange: float
    postMarketChangePercent: float

    preMarketPrice: float
    preMarketChange: float
    preMarketChangePercent: float


    def __str__(self) -> str:
        rockets: str = '🚀' * floor(self.totalChangePercent / 5)
        message: str = f"🔸 {self.displayName} ${self.symbol.upper()} {rockets}\n"

        if 'preMarketPrice' in dir(self):
            if (float(self.preMarketChangePercent) > 0):
                emoji = '📈'
            else:
                emoji = '📉'
            message += f"<b>Pre Market</b> {emoji}\n" \
                f"{self.preMarketPrice}$ " \
                f"({self.preMarketChange}$, {self.preMarketChangePercent}%)\n"

        if 'regularMarketPrice' in dir(self):
            if (float(self.regularMarketChangePercent) > 0):
                emoji = '📈'
            else:
                emoji = '📉'
            message += f"<b>Regular Market</b> {emoji}\n" \
                f"{self.regularMarketPrice}$ " \
                f"({self.regularMarketChange}$, {self.regularMarketChangePercent}%)\n"

        if 'postMarketPrice' in dir(self):
            if (float(self.postMarketChangePercent) > 0):
                emoji = '📈'
            else:
                emoji = '📉'
            message += f"<b>After Hours</b> {emoji}\n" \
                f"{self.postMarketPrice}$ " \
                f"({self.postMarketChange}$, {self.postMarketChangePercent}%)\n"

        return message

    def __init__(self, obj) -> None:
        self.symbol = obj['symbol']
        self.displayName = obj['displayName'] or obj['longName'] or obj['shortName']
        self.totalChangePercent = 0

        if 'regularMarketPrice' in obj:
            self.regularMarketPrice = format(
                round(obj['regularMarketPrice'], 2))
            self.regularMarketChange = format(
                round(obj['regularMarketChange'], 2))
            self.regularMarketChangePercent = format(
                round(obj['regularMarketChangePercent'], 2))
            self.totalChangePercent += float(obj['regularMarketChangePercent'])

        if 'postMarketPrice' in obj:
            self.postMarketPrice = format(
                round(obj['postMarketPrice'], 2))
            self.postMarketChange = format(
                round(obj['postMarketChange'], 2))
            self.postMarketChangePercent = format(
                round(obj['postMarketChangePercent'], 2))
            self.totalChangePercent += float(obj['postMarketChangePercent'])

        if 'preMarketPrice' in obj:
            self.preMarketPrice = format(
                round(obj['preMarketPrice'], 2))
            self.preMarketChange = format(
                round(obj['preMarketChange'], 2))
            self.preMarketChangePercent = format(
                round(obj['preMarketChangePercent'], 2))
            self.totalChangePercent += float(obj['preMarketChangePercent'])
