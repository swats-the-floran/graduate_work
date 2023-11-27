import datetime
import sqlite3
from typing import Any


def dict_factory(cursor: sqlite3.Cursor, row: tuple[Any]) -> dict[str, Any]:
    dictionary = {}
    for idx, col in enumerate(cursor.description):
        dictionary[col[0]] = row[idx]
    return dictionary


def make_datetime(datetime_: str | datetime.datetime) -> datetime.datetime:
    if isinstance(datetime_, datetime.datetime):
        return datetime_
    datetime_ = datetime_.replace("+00", "+0000")
    return datetime.datetime.strptime(datetime_, "%Y-%m-%d %H:%M:%S.%f%z")


def make_date(date_: str | datetime.date) -> datetime.date:
    if date_ is None:
        return None
    elif isinstance(date_, datetime.date):
        return date_
    return datetime.datetime.strptime(date_, "%Y-%m-%d").date()
