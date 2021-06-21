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
    totalChangePercent: float = 0.0

    regularMarketPrice: float = 0.0
    regularMarketChange: float = 0.0
    regularMarketChangePercent: float = 0.0

    postMarketPrice: float = 0.0
    postMarketChange: float = 0.0
    postMarketChangePercent: float = 0.0

    preMarketPrice: float = 0.0
    preMarketChange: float = 0.0
    preMarketChangePercent: float = 0.0

    def getLatestPrice(self) -> float:
        return self.preMarketPrice or self.postMarketPrice or self.regularMarketPrice

    def __str__(self) -> str:
        rockets: str = '🚀' * floor(self.totalChangePercent / 5)
        message: str = f"🔸 {self.displayName} ${self.symbol.upper()} {rockets}\n"

        if self.preMarketPrice:
            if (self.preMarketChangePercent > 0):
                emoji = '📈'
            else:
                emoji = '📉'
            message += f"<b>Pre Market</b> {emoji}\n" \
                f"{self.preMarketPrice}$ " \
                f"({self.preMarketChange}$, {self.preMarketChangePercent}%)\n"

        if self.regularMarketPrice:
            if (self.regularMarketChangePercent > 0):
                emoji = '📈'
            else:
                emoji = '📉'
            message += f"<b>Regular Market</b> {emoji}\n" \
                f"{self.regularMarketPrice}$ " \
                f"({self.regularMarketChange}$, {self.regularMarketChangePercent}%)\n"

        if self.postMarketPrice:
            if (self.postMarketChangePercent > 0):
                emoji = '📈'
            else:
                emoji = '📉'
            message += f"<b>After Hours</b> {emoji}\n" \
                f"{self.postMarketPrice}$ " \
                f"({self.postMarketChange}$, {self.postMarketChangePercent}%)\n"

        return message

    def __init__(self, obj) -> None:
        self.symbol = obj['symbol']

        for prop in ['displayName', 'shortName', 'longName']:
            if prop in obj:  
                self.displayName = obj[prop]
                break

        if not self.displayName:
            raise ValueError('Stock name not found')

        if 'regularMarketPrice' in obj:
            self.regularMarketPrice = float(format(
                round(obj['regularMarketPrice'], 2)))
            self.regularMarketChange = float(format(
                round(obj['regularMarketChange'], 2)))
            self.regularMarketChangePercent = float(format(
                round(obj['regularMarketChangePercent'], 2)))
            self.totalChangePercent += float(obj['regularMarketChangePercent'])

        if 'postMarketPrice' in obj:
            self.postMarketPrice = float(format(
                round(obj['postMarketPrice'], 2)))
            self.postMarketChange = float(format(
                round(obj['postMarketChange'], 2)))
            self.postMarketChangePercent = float(format(
                round(obj['postMarketChangePercent'], 2)))
            self.totalChangePercent += float(obj['postMarketChangePercent'])

        if 'preMarketPrice' in obj:
            self.preMarketPrice = float(format(
                round(obj['preMarketPrice'], 2)))
            self.preMarketChange = float(format(
                round(obj['preMarketChange'], 2)))
            self.preMarketChangePercent = float(format(
                round(obj['preMarketChangePercent'], 2)))
            self.totalChangePercent += float(obj['preMarketChangePercent'])
