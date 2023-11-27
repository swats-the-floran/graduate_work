from clickhouse_driver import Client

from config import BaseConfig

settings = BaseConfig()

DB_NAME = settings.DB_NAME
BOOKMARKS_TABLE_NAME = settings.BOOKMARKS_TABLE_NAME
FILM_RATINGS_TABLE_NAME = settings.FILM_RATINGS_TABLE_NAME
REVIEW_RATINGS_TABLE_NAME = settings.REVIEW_RATINGS_TABLE_NAME
REVIEWS_TABLE_NAME = settings.REVIEWS_TABLE_NAME
VIEWS_TABLE_NAME = settings.VIEWS_TABLE_NAME

clickhouse_client = Client(host=settings.CLICKHOUSE_HOST)


def create_clickhouse_tables():
    clickhouse_client.execute(f'CREATE DATABASE IF NOT EXISTS {DB_NAME} ON CLUSTER company_cluster')

    clickhouse_client.execute(f'''
        CREATE TABLE IF NOT EXISTS {DB_NAME}.{VIEWS_TABLE_NAME} ON CLUSTER company_cluster (
            user_id INT,
            movie_id INT,
            chunk INT
        )
        Engine=MergeTree()
        ORDER BY (user_id)
    ''')

    clickhouse_client.execute(f'''
        CREATE TABLE IF NOT EXISTS {DB_NAME}.{FILM_RATINGS_TABLE_NAME} ON CLUSTER company_cluster (
            user_id INT,
            movie_id INT,
            score Int8
        )
        Engine=MergeTree()
        ORDER BY (user_id)
    ''')

    clickhouse_client.execute(f'''
        CREATE TABLE IF NOT EXISTS {DB_NAME}.{REVIEWS_TABLE_NAME} ON CLUSTER company_cluster (
            user_id INT,
            movie_id INT,
            review_text TEXT,
            score Int8,
            timestamp DATETIME
        )
        Engine=MergeTree()
        ORDER BY (user_id)
    ''')

    clickhouse_client.execute(f'''
        CREATE TABLE IF NOT EXISTS {DB_NAME}.{REVIEW_RATINGS_TABLE_NAME} ON CLUSTER company_cluster (
            user_id INT,
            author_id INT,
            movie_id INT,
            score Int8
        )
        Engine=MergeTree()
        ORDER BY (user_id)
    ''')

    clickhouse_client.execute(f'''
        CREATE TABLE IF NOT EXISTS {DB_NAME}.{BOOKMARKS_TABLE_NAME} ON CLUSTER company_cluster (
            user_id INT,
            movie_id INT
        )
        Engine=MergeTree()
        ORDER BY (user_id)
    ''')


if __name__ == '__main__':
    create_clickhouse_tables()
