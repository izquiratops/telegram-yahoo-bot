from tinydb import TinyDB, Query
from dataclasses import dataclass, asdict

TinyDB.DEFAULT_TABLE_KWARGS = {'cache_size': 30}


@dataclass
class Alert:
    '''A module-level docstring

    Notice the comment above the docstring specifying the encoding.
    Docstrings do appear in the bytecode, so you can access this through
    the ``__doc__`` attribute. This is also what you'll see if you call
    help() on a module or any other Python object.
    '''
    symbol: str
    reference_point: float
    target_point: float

    def __str__(self) -> str:
        return f'{self.symbol.upper()} @{self.target_point}'

    def __init__(self, dictionary: dict):
        for k, v in dictionary.items():
            setattr(self, k, v)


@dataclass
class AlertService:
    '''A module-level docstring

    Notice the comment above the docstring specifying the encoding.
    Docstrings do appear in the bytecode, so you can access this through
    the ``__doc__`` attribute. This is also what you'll see if you call
    help() on a module or any other Python object.
    '''

    def create_alert(self, chat_id: str, alert: Alert) -> None:
        table = self.db.table(chat_id)
        table.insert(asdict(alert))

    def get_alerts(self, chat_id: str) -> list:
        table = self.db.table(chat_id)
        alerts = [Alert(alert) for alert in table.all()]
        return alerts

    def remove_alert(self, chat_id: str, alert: Alert) -> None:
        table = self.db.table(chat_id)
        try:
            table.remove(Query().fragment(asdict(alert)))
        except IndexError:
            print('(!) --> Hey this failed')
            pass

    def search_by_symbol_and_target(self, chat_id: str, symbol: str, target_point: float) -> list:
        table = self.db.table(chat_id)

        # Saved always as lowercase
        symbol = symbol.lower()
        results = table.search(Query().fragment({
            'symbol': symbol,
            'target_point': target_point
        }))
        return results

    def __init__(self) -> None:
        self.db = TinyDB('database.json')
