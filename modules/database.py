from dataclasses import asdict
from typing import List
from tinydb import TinyDB, Query

from modules.model.alert import Alert

TinyDB.DEFAULT_TABLE_KWARGS = {'cache_size': 30}


class DatabaseService:
    def create_alert(self, chat_id: str, alert: Alert) -> None:
        table = self.db.table(chat_id)
        table.insert(asdict(alert))

    def get_length(self, chat_id: str) -> int:
        table = self.db.table(chat_id)
        return len(table)

    def get_alerts(self, chat_id: str) -> List[str]:
        table = self.db.table(chat_id)
        try:
            res = table.all()
            alerts = [Alert(alert) for alert in res]
        except:
            raise

        # Sorting
        target_sorted_alerts = sorted(
            alerts, key=lambda x: x.target_point)
        symbol_sorted_alerts = sorted(
            target_sorted_alerts, key=lambda x: x.symbol)

        return symbol_sorted_alerts

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

    def __init__(self, path: str = 'database.json') -> None:
        self.db = TinyDB(path)
