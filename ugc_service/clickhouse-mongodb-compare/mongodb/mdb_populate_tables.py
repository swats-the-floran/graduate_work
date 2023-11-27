from datetime import datetime
from random import randint
from time import sleep

from pymongo import MongoClient

from config import BaseConfig

settings = BaseConfig()

DB_NAME = settings.DB_NAME
BOOKMARKS_TABLE_NAME = settings.BOOKMARKS_TABLE_NAME
FILM_RATINGS_TABLE_NAME = settings.FILM_RATINGS_TABLE_NAME
REVIEW_RATINGS_TABLE_NAME = settings.REVIEW_RATINGS_TABLE_NAME
REVIEWS_TABLE_NAME = settings.REVIEWS_TABLE_NAME
VIEWS_TABLE_NAME = settings.VIEWS_TABLE_NAME

mdb_client = MongoClient(settings.MONGODB_HOST)
mdb_db = mdb_client[DB_NAME]


def populate_bookmarks():
    collection = mdb_db[BOOKMARKS_TABLE_NAME]

    for movie_id in range(1, 201):
        data = []

        for user_id in range(1, 1001):
            data.append({
                'user_id': user_id,
                'movie_id': movie_id,
            })

        collection.insert_many(data)
        sleep(3)
        break


def populate_film_ratings():
    collection = mdb_db[FILM_RATINGS_TABLE_NAME]

    for movie_id in range(1, 201):
        data = []

        for user_id in range(1, 1001):
            score = randint(0, 10)
            data.append({
                'user_id': user_id,
                'movie_id': movie_id,
                'score': score,
            })

        collection.insert_many(data)
        sleep(3)
        break


def populate_review_ratings():
    collection = mdb_db[REVIEW_RATINGS_TABLE_NAME]

    for movie_id in range(1, 201):
        data = []

        for user_id in range(1, 1001):
            for author_id in (1, 1001):
                score = randint(0, 10)

                data.append({
                    'user_id': user_id,
                    'author_id': author_id,
                    'movie_id': movie_id,
                    'score': score,
                })

        collection.insert_many(data)
        sleep(3)
        break


def populate_reviews():
    collection = mdb_db[REVIEWS_TABLE_NAME]
    review_text = "The db.collection.drop method's behavior differs from the driver's drop method's behavior. The driver's connection must have automatic encryption enabled in order to drop both the specified collection and any internal collections related to encrypted fields. mongosh always drops the specified collection and any internal collections related to encrypted fields."

    for movie_id in range(1, 201):
        data = []

        for user_id in range(1, 1001):
            score = randint(0, 10)
            timestamp = datetime.now()

            data.append({
                'user_id': user_id,
                'movie_id': movie_id,
                'review_text': review_text,
                'score': score,
                'timestamp': timestamp,
            })

        collection.insert_many(data)
        sleep(3)
        break


def populate_views():
    collection = mdb_db[VIEWS_TABLE_NAME]

    for movie_id in range(1, 201):
        data = []

        for user_id in range(1, 1001):
            for chunk in range(1, 61):
                data.append({
                    'user_id': user_id,
                    'movie_id': movie_id,
                    'chunk': chunk,
                })

        collection.insert_many(data)
        sleep(3)
        break


def populate_all():
    populate_bookmarks()
    populate_film_ratings()
    populate_review_ratings()
    populate_reviews()
    populate_views()


if __name__ == '__main__':
    populate_all()

