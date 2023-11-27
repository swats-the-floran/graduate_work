from typing import Iterator, Type

import psycopg2
from errors import SaveDBException
from models import BaseModel
from psycopg2.extensions import connection as Connection
from psycopg2.extras import execute_values


class PostgresRepository:
    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    def get_count(self, model: Type[BaseModel]) -> int:
        with self._connection.cursor() as cursor:
            cursor.execute(f"SELECT COUNT(*) FROM content.{model.Config.table_name}")
            return cursor.fetchone()[0]

    def get_all(self, model: Type[BaseModel], order_by: str | None = None) -> list[BaseModel]:
        fileds_name = model.keys_to_psql()
        query = f"SELECT {fileds_name} FROM content.{model.Config.table_name}"
        if order_by:
            query += f" ORDER BY {order_by}"

        with self._connection.cursor() as cursor:
            cursor.execute(query)
            return [model.from_dict(result) for result in cursor.fetchall()]

    def save_all(self, model: Type[BaseModel], models: Iterator[BaseModel]) -> None:
        table_name = model.Config.table_name
        field_names = model.keys_to_psql()
        with self._connection.cursor() as cursor:
            try:
                execute_values(
                    cur=cursor,
                    sql=f"INSERT INTO content.{table_name} ({field_names}) VALUES %s",
                    argslist=[model.values for model in models],
                )
            except psycopg2.Error as exc:
                raise SaveDBException(f"An error occurred while saving: {exc}")

    def commit(self) -> None:
        self._connection.commit()
