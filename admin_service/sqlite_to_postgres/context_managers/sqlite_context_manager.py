import sqlite3
from typing import Callable


class SQLiteContextManager:
    def __init__(self, db_url: str, cursor_factory: Callable | None = None) -> None:
        self._connection = sqlite3.connect(db_url)
        if cursor_factory:
            self._connection.row_factory = cursor_factory

    def __enter__(self) -> sqlite3.Connection:
        return self._connection

    def __exit__(self, type, value, traceback) -> None:
        self._connection.close()


class SQLiteCursorContextManager:
    def __init__(self, cursor: sqlite3.Cursor) -> None:
        self._cursor = cursor

    def __enter__(self) -> sqlite3.Cursor:
        return self._cursor

    def __exit__(self, type, value, traceback) -> None:
        self._cursor.close()
