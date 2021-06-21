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
        return f'{self.symbol.upper()} {self.target_point}'

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
        price_sorted_alerts = sorted(alerts, key=lambda x: x.target_point)
        return sorted(price_sorted_alerts, key=lambda x: x.symbol)

    def remove_alert(self, chat_id: str, alert: Alert) -> None:
        table = self.db.table(chat_id)
        try:
            table.remove(Query().fragment(asdict(alert)))
        except IndexError:
            raise

    def search_markup_response(self, chat_id: str, symbol: str, target_point: str) -> Alert:
        table = self.db.table(chat_id)
        result = table.get(
            (Query().symbol == symbol) & 
            (Query().target_point == target_point))
        try:
            return Alert(result)
        except:
            raise

    def __init__(self) -> None:
        self.db = TinyDB('database.json')
