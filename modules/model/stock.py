from math import ceil
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
    display_name: str
    total_change_percent: float = 0.0

    regular_market_price: float = 0.0
    regularMarketChange: float = 0.0
    regular_market_change_percent: float = 0.0

    post_market_price: float = 0.0
    post_market_change: float = 0.0
    post_market_change_percent: float = 0.0

    pre_market_price: float = 0.0
    pre_market_change: float = 0.0
    pre_market_change_percent: float = 0.0

    def get_latest_price(self) -> float:
        return self.pre_market_price or self.post_market_price or self.regular_market_price

    def get_change_emojis(self, value: float) -> str:
        degree = value / 5
        isPossitive = degree > 0
        absolute_value = ceil(abs(degree))

        if (isPossitive > 0):
            return '🚀' * absolute_value
        else:
            return '💀' * absolute_value

    def __str__(self) -> str:
        link = f"<a href='https://www.google.com/search?q={self.symbol}+stock'>{self.display_name}</a>"
        message: str = f"👉 {self.symbol.upper()} · {link}\n"

        if self.pre_market_price:
            emojis = self.get_change_emojis(self.pre_market_change_percent)
            message += f"<b>Pre Market</b> {emojis}\n" \
                f"{self.pre_market_price}$ " \
                f"({self.pre_market_change}$, {self.pre_market_change_percent}%)\n"

        if self.regular_market_price:
            emojis = self.get_change_emojis(self.regular_market_change_percent)
            message += f"<b>Regular Market</b> {emojis}\n" \
                f"{self.regular_market_price}$ " \
                f"({self.regularMarketChange}$, {self.regular_market_change_percent}%)\n"

        if self.post_market_price:
            emojis = self.get_change_emojis(self.post_market_change_percent)
            message += f"<b>After Hours</b> {emojis}\n" \
                f"{self.post_market_price}$ " \
                f"({self.post_market_change}$, {self.post_market_change_percent}%)\n"

        return message

    def __init__(self, obj) -> None:
        self.symbol = obj['symbol']

        for prop in ['displayName', 'shortName', 'longName']:
            if prop in obj:
                self.display_name = obj[prop]
                break

        if not self.display_name:
            raise ValueError('Stock name not found')

        if 'regularMarketPrice' in obj:
            self.regular_market_price = float(format(
                round(obj['regularMarketPrice'], 2)))
            self.regularMarketChange = float(format(
                round(obj['regularMarketChange'], 2)))
            self.regular_market_change_percent = float(format(
                round(obj['regularMarketChangePercent'], 2)))
            self.total_change_percent += float(
                obj['regularMarketChangePercent'])

        if 'postMarketPrice' in obj:
            self.post_market_price = float(format(
                round(obj['postMarketPrice'], 2)))
            self.post_market_change = float(format(
                round(obj['postMarketChange'], 2)))
            self.post_market_change_percent = float(format(
                round(obj['postMarketChangePercent'], 2)))
            self.total_change_percent += float(obj['postMarketChangePercent'])

        if 'preMarketPrice' in obj:
            self.pre_market_price = float(format(
                round(obj['preMarketPrice'], 2)))
            self.pre_market_change = float(format(
                round(obj['preMarketChange'], 2)))
            self.pre_market_change_percent = float(format(
                round(obj['preMarketChangePercent'], 2)))
            self.total_change_percent += float(obj['preMarketChangePercent'])
