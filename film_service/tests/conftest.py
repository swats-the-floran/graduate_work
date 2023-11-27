from typing import Any

import pytest
from elastic_transport import ApiResponseMeta
from elasticsearch import NotFoundError

from models.models import Movie


@pytest.fixture()
def es_index_movie_one() -> dict[str, Any]:
    return {
        "_index": "movies",
        "_id": "3bdae84f-9a04-4b04-9f7c-c05582d529e5",
        "_score": None,
        "_source": {
            "id": "3bdae84f-9a04-4b04-9f7c-c05582d529e5",
            "imdb_rating": 7.2,
            "title": "Star Wars: Qui-Gon Jinn III",
            "description": (
                "The Jedi temple gets attacked by an army of Siths. "
                "It's up to Qui-Gon Jinn and Obi-Wan Kenobi to stop the invasion. "
                "Meanwhile Darth Sidious seeks after a new apprentice."
            ),
            "genres_name": ["Action", "Sci-Fi"],
            "directors_name": ["David Anghel", "Pauli Janhunen Calderón"],
            "actors_names": [
                "David Anghel",
                "Emilio Janhunen Calderón",
                "Marina Janhunen Calderón",
                "Pauli Janhunen Calderón",
            ],
            "writers_names": ["David Anghel"],
            "genres": [
                {"id": "3d8d9bf5-0d90-4353-88ba-4ccc5d2c07ff", "name": "Action"},
                {"id": "6c162475-c7ed-4461-9184-001ef3d9f26e", "name": "Sci-Fi"},
            ],
            "directors": [
                {"id": "06c281cf-c2be-46b7-930c-8f4975f07b02", "name": "David Anghel"},
                {"id": "08524e56-38a3-411a-8c30-dfca9b54aca0", "name": "Pauli Janhunen Calderón"},
            ],
            "actors": [
                {"id": "06c281cf-c2be-46b7-930c-8f4975f07b02", "name": "David Anghel"},
                {"id": "08524e56-38a3-411a-8c30-dfca9b54aca0", "name": "Pauli Janhunen Calderón"},
                {"id": "b35228ed-88b4-4f64-90c4-00d4953c053b", "name": "Emilio Janhunen Calderón"},
                {"id": "e84b46b0-1623-41d1-8ab8-26db182d1261", "name": "Marina Janhunen Calderón"},
            ],
            "writers": [{"id": "06c281cf-c2be-46b7-930c-8f4975f07b02", "name": "David Anghel"}],
        },
    }


@pytest.fixture()
def default_movie(es_index_movie_one) -> Movie:
    return Movie(**es_index_movie_one["_source"])


@pytest.fixture()
def not_found_error_from_es() -> NotFoundError:
    return NotFoundError(
        message="Test raise",
        meta=ApiResponseMeta(status=404, http_version="1.1", headers={}, duration=0.0, node={}),
        body={},
    )


@pytest.fixture()
def es_index_search_movies() -> dict[str, Any]:
    return {
        "hits": {
            "hits": [
                {
                    "_index": "movies",
                    "_id": "3bdae84f-9a04-4b04-9f7c-c05582d529e5",
                    "_score": None,
                    "_source": {
                        "id": "3bdae84f-9a04-4b04-9f7c-c05582d529e5",
                        "imdb_rating": 7.2,
                        "title": "Star Wars: Qui-Gon Jinn III",
                        "description": (
                            "The Jedi temple gets attacked by an army of Siths. "
                            "It's up to Qui-Gon Jinn and Obi-Wan Kenobi to stop the invasion. "
                            "Meanwhile Darth Sidious seeks after a new apprentice."
                        ),
                        "genres_name": ["Action", "Sci-Fi"],
                        "directors_name": ["David Anghel", "Pauli Janhunen Calderón"],
                        "actors_names": [
                            "David Anghel",
                            "Emilio Janhunen Calderón",
                            "Marina Janhunen Calderón",
                            "Pauli Janhunen Calderón",
                        ],
                        "writers_names": ["David Anghel"],
                        "genres": [
                            {"id": "3d8d9bf5-0d90-4353-88ba-4ccc5d2c07ff", "name": "Action"},
                            {"id": "6c162475-c7ed-4461-9184-001ef3d9f26e", "name": "Sci-Fi"},
                        ],
                        "directors": [
                            {"id": "06c281cf-c2be-46b7-930c-8f4975f07b02", "name": "David Anghel"},
                            {"id": "08524e56-38a3-411a-8c30-dfca9b54aca0", "name": "Pauli Janhunen Calderón"},
                        ],
                        "actors": [
                            {"id": "06c281cf-c2be-46b7-930c-8f4975f07b02", "name": "David Anghel"},
                            {"id": "08524e56-38a3-411a-8c30-dfca9b54aca0", "name": "Pauli Janhunen Calderón"},
                            {"id": "b35228ed-88b4-4f64-90c4-00d4953c053b", "name": "Emilio Janhunen Calderón"},
                            {"id": "e84b46b0-1623-41d1-8ab8-26db182d1261", "name": "Marina Janhunen Calderón"},
                        ],
                        "writers": [{"id": "06c281cf-c2be-46b7-930c-8f4975f07b02", "name": "David Anghel"}],
                    },
                },
                {
                    "_index": "movies",
                    "_id": "05d7341e-e367-4e2e-acf5-4652a8435f93",
                    "_score": None,
                    "_source": {
                        "id": "05d7341e-e367-4e2e-acf5-4652a8435f93",
                        "imdb_rating": 9.5,
                        "title": "The Secret World of Jeffree Star",
                        "description": (
                            "Shane Dawson interviews and spends a day with one of the most interesting and "
                            "controversial people on the internet, Jeffrey Star, in a five part series."
                        ),
                        "genres_name": ["Documentary"],
                        "directors_name": [],
                        "actors_names": ["Jeffree Star", "Shane Dawson"],
                        "writers_names": [],
                        "genres": [{"id": "6d141ad2-d407-4252-bda4-95590aaf062a", "name": "Documentary"}],
                        "directors": [],
                        "actors": [
                            {"id": "901595ba-4278-4224-b04c-974c28428a08", "name": "Shane Dawson"},
                            {"id": "99a9ef8f-c45d-44b3-ab09-e39685e011f5", "name": "Jeffree Star"},
                        ],
                        "writers": [],
                    },
                },
            ]
        }
    }


@pytest.fixture()
def desc_es_index_search_movies(es_index_search_movies: dict[str, Any]) -> dict[str, Any]:
    es_index_search_movies["hits"]["hits"].sort(key=lambda k: k["_source"]["imdb_rating"], reverse=True)
    return es_index_search_movies


@pytest.fixture()
def es_index_search_movies_genre_action(es_index_search_movies: dict[str, Any]) -> dict[str, Any]:
    del es_index_search_movies["hits"]["hits"][1]
    return es_index_search_movies


@pytest.fixture()
def search_movies_fixture(es_index_search_movies) -> list[Movie]:
    return [Movie(**movie["_source"]) for movie in es_index_search_movies["hits"]["hits"]]


@pytest.fixture()
def find_movies_by_genre_action(es_index_search_movies) -> list[Movie]:
    action_movies = []
    for movie in es_index_search_movies["hits"]["hits"]:
        for genre in movie["_source"]["genres"]:
            if genre["id"] == "3d8d9bf5-0d90-4353-88ba-4ccc5d2c07ff":
                action_movies.append(movie)

    return [Movie(**movie["_source"]) for movie in action_movies]


@pytest.fixture()
def es_index_persons() -> dict:
    return {
        "hits": {
            "hits": [
                {
                    "_index": "persons",
                    "_id": "25168644-d9e1-4a5c-ab1b-ff03f1209430",
                    "_score": 4.1300764,
                    "_source": {"id": "25168644-d9e1-4a5c-ab1b-ff03f1209430", "name": "Thomas C. Bartley Jr."},
                },
                {
                    "_index": "persons",
                    "_id": "4e3a98f9-02a2-43e3-a76a-8414efead960",
                    "_score": 4.8148403,
                    "_source": {"id": "4e3a98f9-02a2-43e3-a76a-8414efead960", "name": "Thomas K. Phillips"},
                },
                {
                    "_index": "persons",
                    "_id": "aa30b9fb-545c-48cd-87ff-cd8b7fafb6ed",
                    "_score": 4.130804,
                    "_source": {"id": "aa30b9fb-545c-48cd-87ff-cd8b7fafb6ed", "name": "David Pursall"},
                },
                {
                    "_index": "persons",
                    "_id": "ae073203-b7e9-4ac9-a537-0c285b98dced",
                    "_score": 4.130804,
                    "_source": {"id": "ae073203-b7e9-4ac9-a537-0c285b98dced", "name": "David Carty"},
                },
            ],
        },
    }
