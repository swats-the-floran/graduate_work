from typing import Any, Callable

import psycopg2
from psycopg2.extensions import connection as Connection


class PostgreSQLContextManager:
    def __init__(self, dsn: dict[str, Any], cursor_factory: Callable | None = None) -> None:
        self._connection = psycopg2.connect(**dsn, cursor_factory=cursor_factory)

    def __enter__(self) -> Connection:
        return self._connection

    def __exit__(self, type, value, traceback) -> None:
        self._connection.close()
