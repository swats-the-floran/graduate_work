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

clickhouse_client = Client(host=settings.CLICKHOUSE_HOST)
existing_tables = clickhouse_client.execute(f'SHOW TABLES FROM {DB_NAME}')

tables = [
    (BOOKMARKS_TABLE_NAME,),
    (FILM_RATINGS_TABLE_NAME,),
    (REVIEW_RATINGS_TABLE_NAME,),
    (REVIEWS_TABLE_NAME,),
    (VIEWS_TABLE_NAME,),
]


@pytest.mark.parametrize("table", tables)
def test_tables_exist(table):
    assert table in existing_tables
