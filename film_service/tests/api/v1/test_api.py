from http import HTTPStatus
from typing import Any
from unittest.mock import AsyncMock

import pytest
from asgi_lifespan import LifespanManager
from elasticsearch import AsyncElasticsearch, NotFoundError
from httpx import AsyncClient
from redis.asyncio import Redis

from main import app


@pytest.fixture(autouse=True)
def redis_mock(mocker):
    mocker.patch.object(Redis, "set", mocker.AsyncMock(return_value=None))
    mocker.patch.object(Redis, "get", mocker.AsyncMock(return_value=None))


@pytest.fixture(autouse=True)
def aes_get_mock(mocker):
    mock = mocker.AsyncMock()
    mocker.patch.object(AsyncElasticsearch, "get", mock)
    return mock


@pytest.fixture(autouse=True)
def aes_search_mock(mocker):
    mock = mocker.AsyncMock()
    mocker.patch.object(AsyncElasticsearch, "search", mock)
    return mock


@pytest.mark.asyncio
async def test_get_movie_by_id(aes_get_mock: AsyncMock, es_index_movie_one: dict[str, Any]) -> None:
    aes_get_mock.return_value = es_index_movie_one

    async with AsyncClient(app=app, base_url="http://test") as api_client, LifespanManager(app):
        response = await api_client.get("/api/v1/films/3bdae84f-9a04-4b04-9f7c-c05582d529e5/")

    assert response.status_code == HTTPStatus.OK
    assert response.json()["uuid"] == "3bdae84f-9a04-4b04-9f7c-c05582d529e5"
    assert response.json()["actors"][0].get("full_name") is not None


@pytest.mark.asyncio
async def test_get_movie_by_id_raise_404(aes_get_mock: AsyncMock, not_found_error_from_es: NotFoundError) -> None:
    aes_get_mock.side_effect = not_found_error_from_es

    async with AsyncClient(app=app, base_url="http://test") as api_client, LifespanManager(app):
        response = await api_client.get("/api/v1/films/00000000-0000-0000-0000-000000000000/")

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()["detail"] == "Movie with id=00000000-0000-0000-0000-000000000000 not found"


@pytest.mark.asyncio
async def test_get_movie_by_id_not_uuid() -> None:
    async with AsyncClient(app=app, base_url="http://test") as api_client, LifespanManager(app):
        response = await api_client.get("/api/v1/films/00000000/")

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert "value is not a valid uuid" in response.json()["detail"][0]["msg"]


@pytest.mark.asyncio
async def test_get_movies_desc(aes_search_mock: AsyncMock, desc_es_index_search_movies: dict) -> None:
    aes_search_mock.return_value = desc_es_index_search_movies

    async with AsyncClient(app=app, base_url="http://test") as api_client, LifespanManager(app):
        response = await api_client.get("/api/v1/films?sort=-imdb_rating&page_size=2&page_number=1")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == [
        {
            "uuid": "05d7341e-e367-4e2e-acf5-4652a8435f93",
            "title": "The Secret World of Jeffree Star",
            "imdb_rating": 9.5,
        },
        {
            "uuid": "3bdae84f-9a04-4b04-9f7c-c05582d529e5",
            "title": "Star Wars: Qui-Gon Jinn III",
            "imdb_rating": 7.2,
        },
    ]


@pytest.mark.asyncio
async def test_get_movies_without_sort(aes_search_mock: AsyncMock, es_index_search_movies: dict) -> None:
    aes_search_mock.return_value = es_index_search_movies

    async with AsyncClient(app=app, base_url="http://test") as api_client, LifespanManager(app):
        response = await api_client.get("/api/v1/films?page_size=2&page_number=1")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == [
        {
            "uuid": "3bdae84f-9a04-4b04-9f7c-c05582d529e5",
            "title": "Star Wars: Qui-Gon Jinn III",
            "imdb_rating": 7.2,
        },
        {
            "uuid": "05d7341e-e367-4e2e-acf5-4652a8435f93",
            "title": "The Secret World of Jeffree Star",
            "imdb_rating": 9.5,
        },
    ]


@pytest.mark.asyncio
async def test_get_movies_sort_uncorrect_field() -> None:
    async with AsyncClient(app=app, base_url="http://test") as api_client, LifespanManager(app):
        response = await api_client.get("/api/v1/films?sort=-uuid?page_size=2&page_number=1")

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert "string does not match regex" in response.json()["detail"][0]["msg"]


@pytest.mark.asyncio
async def test_get_movies_genre(aes_search_mock: AsyncMock, es_index_search_movies_genre_action: dict) -> None:
    aes_search_mock.return_value = es_index_search_movies_genre_action

    async with AsyncClient(app=app, base_url="http://test") as api_client, LifespanManager(app):
        response = await api_client.get(
            "/api/v1/films?genre=40f95fa9-7088-492f-bcf6-024e7c83cb09&sort=-imdb_rating&page_size=2&page_number=1"
        )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == [
        {
            "uuid": "3bdae84f-9a04-4b04-9f7c-c05582d529e5",
            "title": "Star Wars: Qui-Gon Jinn III",
            "imdb_rating": 7.2,
        },
    ]


@pytest.mark.asyncio
async def test_get_movies_genre_empty_list(aes_search_mock: AsyncMock) -> None:
    aes_search_mock.return_value = {"hits": {"hits": []}}

    async with AsyncClient(app=app, base_url="http://test") as api_client, LifespanManager(app):
        response = await api_client.get(
            "/api/v1/films?genre=40f95fa9-7088-492f-bcf6-024e7c83cb09&sort=-imdb_rating&page_size=2&page_number=1"
        )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == []


@pytest.mark.asyncio
async def test_search(aes_search_mock: AsyncMock, es_index_search_movies: dict) -> None:
    aes_search_mock.return_value = es_index_search_movies

    async with AsyncClient(app=app, base_url="http://test") as api_client, LifespanManager(app):
        response = await api_client.get("/api/v1/films/search/?query=star&page_size=2&page_number=1")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == [
        {
            "uuid": "3bdae84f-9a04-4b04-9f7c-c05582d529e5",
            "title": "Star Wars: Qui-Gon Jinn III",
            "imdb_rating": 7.2,
        },
        {
            "uuid": "05d7341e-e367-4e2e-acf5-4652a8435f93",
            "title": "The Secret World of Jeffree Star",
            "imdb_rating": 9.5,
        },
    ]
