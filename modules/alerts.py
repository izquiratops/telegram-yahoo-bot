from tinydb import TinyDB, Query
from dataclasses import dataclass

TinyDB.DEFAULT_TABLE_KWARGS = {'cache_size': 30}

@dataclass
class Alarm:
    symbol: str
    kind: str
    threshold: float

@dataclass
class AlertService:
    '''A module-level docstring

    Notice the comment above the docstring specifying the encoding.
    Docstrings do appear in the bytecode, so you can access this through
    the ``__doc__`` attribute. This is also what you'll see if you call
    help() on a module or any other Python object.
    '''

    def create_alarm(self, name: int) -> None:
        # table = self.db.table(name)
        return

    def get_alarms(self, name: int) -> list:
        table = self.db.table(name)
        return table.all()

    def remove_alert(self, name: int) -> None:
        return

    def remove_alarm(self, name: int) -> None:
        return

    def __init__(self) -> None:
        self.db = TinyDB('database.json')
