import json
import logging
from contextlib import contextmanager
from typing import Iterator

import elasticsearch.exceptions
from elasticsearch import ConnectionError, Elasticsearch, helpers

from utils.backoff import backoff

from .index import Index


@contextmanager
def es_connection(dsn: str) -> Iterator:
    connection = Elasticsearch(dsn)
    try:
        yield connection
    finally:
        connection.close()


class EsLoader:
    def __init__(self, elastic_dsn, logger: logging.Logger, index: Index) -> None:
        self.dsn = elastic_dsn
        self.logger = logger
        self.index = index
        self.create_index()

    @backoff((ConnectionError,))
    def create_index(self) -> None:
        with es_connection(self.dsn) as es:
            if not es.ping():
                raise elasticsearch.exceptions.ConnectionError

            if not es.indices.exists(index=self.index.name):
                es.indices.create(index=self.index.name, settings=self.index.settings, mappings=self.index.mappings)
                self.logger.info(
                    "Create index %s: settings:%s and mappings:%s",
                    self.index.name,
                    json.dumps(self.index.settings, indent=2),
                    json.dumps(self.index.mappings, indent=2),
                )

    def load_data_to_index(self, data: list[dict]) -> None:
        actions = [{"_index": self.index.name, "_id": row["id"], "_source": row} for row in data]
        with es_connection(self.dsn) as es:
            helpers.bulk(es, actions, stats_only=True)
            self.logger.info("Loaded %s %s", len(data), self.index.name)
