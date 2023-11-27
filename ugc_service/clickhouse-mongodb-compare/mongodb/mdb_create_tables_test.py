import pytest
from pymongo import MongoClient

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

client = MongoClient(host=settings.MONGODB_HOST)
db = client[DB_NAME]
existing_tables = db.list_collection_names()


@pytest.mark.parametrize("table", tables)
def test_tables_exist(table):
    assert table in existing_tables
