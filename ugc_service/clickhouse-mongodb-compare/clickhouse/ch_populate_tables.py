from datetime import datetime
from random import randint
from time import sleep

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


def populate_bookmarks():
    for movie_id in range(1, 201):
        query_string = f'INSERT INTO {DB_NAME}.{BOOKMARKS_TABLE_NAME} (user_id, movie_id) VALUES '

        for user_id in range(1, 1001):
            query_string += f' ({user_id}, {movie_id}), '

        clickhouse_client.execute(query_string[:-2])
        sleep(1)


def populate_film_ratings():
    for movie_id in range(1, 201):
        query_string = f'INSERT INTO {DB_NAME}.{FILM_RATINGS_TABLE_NAME} (user_id, movie_id, score) VALUES '

        for user_id in range(1, 1001):
            score = randint(0, 10)
            query_string += f' ({user_id}, {movie_id}, {score}), '

        clickhouse_client.execute(query_string[:-2])
        sleep(1)


def populate_review_ratings():
    for movie_id in range(1, 201):
        query_string = f'INSERT INTO {DB_NAME}.{REVIEW_RATINGS_TABLE_NAME} (user_id, author_id, movie_id, score) VALUES '

        for user_id in range(1, 1001):
            for author_id in (1, 1001):
                score = randint(0, 10)
                query_string += f' ({user_id}, {author_id}, {movie_id}, {score}), '

        clickhouse_client.execute(query_string[:-2])
        sleep(1)


def populate_reviews():
    review_text_ = 'fuuuuuuuuck'

    for movie_id in range(1, 201):
        query_string = f'INSERT INTO {DB_NAME}.{REVIEWS_TABLE_NAME} (user_id, movie_id, review_text, score, timestamp) VALUES '

        for user_id in range(1, 1001):
            score = randint(0, 10)
            timestamp = str(datetime.now())[:-7]
            query_string += f" ({user_id}, {movie_id}, '{review_text_}', {score}, '{timestamp}'), "

        clickhouse_client.execute(query_string[:-2])
        sleep(1)


def populate_views():
    for movie_id in range(1, 201):
        query_string = f'INSERT INTO {DB_NAME}.{VIEWS_TABLE_NAME} (user_id, movie_id, chunk) VALUES '

        for user_id in range(1, 1001):
            for chunk in range(1, 61):
                query_string += f' ({user_id}, {movie_id}, {chunk}), '

        clickhouse_client.execute(query_string[:-2])
        sleep(1)


def populate_all():
    populate_bookmarks()
    populate_film_ratings()
    populate_review_ratings()
    populate_reviews()
    populate_views()


if __name__ == '__main__':
    populate_all()

