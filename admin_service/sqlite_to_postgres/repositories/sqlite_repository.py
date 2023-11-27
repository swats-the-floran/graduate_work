import sqlite3
from typing import Iterator, Type

from context_managers import SQLiteCursorContextManager
from errors import SelectDBException
from models import BaseModel


class SQLiteRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def get_count(self, model: Type[BaseModel]) -> int:
        with SQLiteCursorContextManager(self._connection.cursor()) as cursor:
            cursor.execute(f"SELECT COUNT(*) as count  FROM {model.Config.table_name}")
            return cursor.fetchone()["count"]

    def get_all(self, model: Type[BaseModel], order_by: str | None = None) -> list[BaseModel]:
        fileds_name = model.get_field_names_for_query_sqlite()
        query = f"SELECT {fileds_name} FROM {model.Config.table_name}"
        if order_by:
            query += f" ORDER BY {order_by}"

        with SQLiteCursorContextManager(self._connection.cursor()) as cursor:
            cursor.execute(query)
            return [model.from_dict(result) for result in cursor.fetchall()]

    def get_all_from_model_batch(
        self,
        model: Type[BaseModel],
        batch_size: int = 100,
    ) -> Iterator[Iterator[BaseModel]]:
        field_names = model.get_field_names_for_query_sqlite()
        return self._batch(
            query=f"SELECT {field_names} FROM {model.Config.table_name}",
            model=model,
            batch_size=batch_size,
        )

    def _batch(
        self,
        query: str,
        model: BaseModel,
        batch_size: int,
    ) -> Iterator[Iterator[BaseModel]]:
        with SQLiteCursorContextManager(self._connection.cursor()) as cursor:
            try:
                cursor.execute(query)
            except Exception as exc:
                raise SelectDBException(f"Data acquisition error {exc}")

            while True:
                if results := cursor.fetchmany(batch_size):
                    yield (model.from_dict(result) for result in results)
                else:
                    break
