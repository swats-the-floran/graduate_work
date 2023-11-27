import abc
import logging
from contextlib import contextmanager
from datetime import datetime
from typing import Iterator

import psycopg2
from psycopg2.extras import RealDictCursor

from etl.loader.index import Index
from utils.state import State

from . import fwq


@contextmanager
def pg_connection(dsn: dict) -> Iterator:
    connection = psycopg2.connect(**dsn, cursor_factory=RealDictCursor)
    connection.set_session(autocommit=True)
    try:
        yield connection
    finally:
        connection.close()


class Extractor(abc.ABC):
    """Выгрузка данных из Postgresql"""

    def __init__(
        self, postgres_dsn, batch_size: int, storage_state: State, logger: logging.Logger, index: Index
    ) -> None:
        self.batch_size = batch_size
        self.state = storage_state
        self.dsn = postgres_dsn
        self.logger = logger
        self.index = index.name

    @abc.abstractmethod
    def query(self) -> str:
        """return query_str"""

    @abc.abstractmethod
    def count_modified(self) -> int:
        """return number of modified"""

    def extract(self, modified: datetime) -> Iterator:
        with pg_connection(self.dsn) as pg_conn, pg_conn.cursor() as cursor:
            query = cursor.mogrify(self.query(), (modified,) * self.count_modified())
            cursor.execute(query)

            while rows := cursor.fetchmany(self.batch_size):
                self.logger.info("Extracted %s %s", len(rows), self.index)
                yield rows

            self.logger.info("No changes in %s detected", self.index)


class MovieExtractor(Extractor):
    def query(self) -> str:
        return fwq.film_work_query

    def count_modified(self) -> int:
        return 3


class GenreExtractor(Extractor):
    def query(self) -> str:
        return fwq.genre_query

    def count_modified(self) -> int:
        return 1


class PersonExtractor(Extractor):
    def query(self) -> str:
        return fwq.person_query

    def count_modified(self) -> int:
        return 1
