import time

import pytest
from clickhouse_driver import Client

from . import config

settings = config.BaseConfig()

DB_NAME = settings.DB_NAME
BOOKMARKS_TABLE_NAME = settings.BOOKMARKS_TABLE_NAME
FILM_RATINGS_TABLE_NAME = settings.FILM_RATINGS_TABLE_NAME
REVIEW_RATINGS_TABLE_NAME = settings.REVIEW_RATINGS_TABLE_NAME
REVIEWS_TABLE_NAME = settings.REVIEWS_TABLE_NAME
VIEWS_TABLE_NAME = settings.VIEWS_TABLE_NAME

tables = [
    BOOKMARKS_TABLE_NAME,
    FILM_RATINGS_TABLE_NAME,
    REVIEW_RATINGS_TABLE_NAME,
    REVIEWS_TABLE_NAME,
    VIEWS_TABLE_NAME,
]

clickhouse_client = Client(host=settings.CLICKHOUSE_HOST)


@pytest.mark.parametrize("table", tables)
def test_records(table):
    assert clickhouse_client.execute(f'SELECT count(*) FROM {DB_NAME}.{table}')[0][0] > 0


@pytest.mark.parametrize("table,user_id", [tables, 666])
def test_timings(table, user_id):
    start_time = time.time()
    clickhouse_client.execute(f'SELECT * FROM {DB_NAME}.{table} WHERE user_id = {user_id}')

    assert time.time() - start_time <= 0.2
