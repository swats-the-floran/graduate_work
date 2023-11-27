import json
from http import HTTPStatus

import aiohttp
import pytest
from redis.asyncio import Redis

from tests.functional.settings import settings


@pytest.mark.functional
@pytest.mark.parametrize(
    ("url", "query_data", "expected_code"),
    [
        (f"{settings.fast_api_dsn}/api/v1/films/search/", {}, HTTPStatus.UNPROCESSABLE_ENTITY),
        (f"{settings.fast_api_dsn}/api/v1/films/search/", {"query": ""}, HTTPStatus.UNPROCESSABLE_ENTITY),
        (
            f"{settings.fast_api_dsn}/api/v1/films/search/",
            {"query": "Star", "page_size": -1},
            HTTPStatus.UNPROCESSABLE_ENTITY,
        ),
        (
            f"{settings.fast_api_dsn}/api/v1/films/search/",
            {"query": "Star", "page_size": 0},
            HTTPStatus.UNPROCESSABLE_ENTITY,
        ),
        (
            f"{settings.fast_api_dsn}/api/v1/films/search/",
            {"query": "Star", "page_size": 1, "page_number": -1},
            HTTPStatus.UNPROCESSABLE_ENTITY,
        ),
        (
            f"{settings.fast_api_dsn}/api/v1/films/search/",
            {"query": "Star", "page_size": 1, "page_number": 0},
            HTTPStatus.UNPROCESSABLE_ENTITY,
        ),
        (
            f"{settings.fast_api_dsn}/api/v1/films/search/",
            {"query": "Star", "page_size": 10, "page_number": 1},
            HTTPStatus.OK,
        ),
        (f"{settings.fast_api_dsn}/api/v1/persons/search/", {}, HTTPStatus.UNPROCESSABLE_ENTITY),
        (f"{settings.fast_api_dsn}/api/v1/persons/search/", {"query": ""}, HTTPStatus.UNPROCESSABLE_ENTITY),
        (
            f"{settings.fast_api_dsn}/api/v1/persons/search/",
            {"query": "Western", "page_size": -1},
            HTTPStatus.UNPROCESSABLE_ENTITY,
        ),
        (
            f"{settings.fast_api_dsn}/api/v1/persons/search/",
            {"query": "Western", "page_size": 0},
            HTTPStatus.UNPROCESSABLE_ENTITY,
        ),
        (
            f"{settings.fast_api_dsn}/api/v1/persons/search/",
            {"query": "Western", "page_size": 1, "page_number": -1},
            HTTPStatus.UNPROCESSABLE_ENTITY,
        ),
        (
            f"{settings.fast_api_dsn}/api/v1/persons/search/",
            {"query": "Western", "page_size": 1, "page_number": 0},
            HTTPStatus.UNPROCESSABLE_ENTITY,
        ),
        (
            f"{settings.fast_api_dsn}/api/v1/persons/search/",
            {"query": "Western", "page_size": 10, "page_number": 1},
            HTTPStatus.OK,
        ),
    ],
)
@pytest.mark.asyncio
async def test_search_check_validate(
    client: aiohttp.ClientSession,
    url: str,
    query_data: dict[str, str | int],
    expected_code: int,
) -> None:
    async with client.get(url, params=query_data) as response:
        got = response.status

    assert got == expected_code


@pytest.mark.functional
@pytest.mark.parametrize(
    ("url", "query_data", "expected_len"),
    [
        (f"{settings.fast_api_dsn}/api/v1/films/search/", {"query": "Star"}, 5),
        (f"{settings.fast_api_dsn}/api/v1/films/search/", {"query": "Star", "page_size": 2, "page_number": 1}, 2),
        (f"{settings.fast_api_dsn}/api/v1/films/search/", {"query": "Star", "page_size": 2, "page_number": 3}, 1),
        (f"{settings.fast_api_dsn}/api/v1/films/search/", {"query": "Star", "page_size": 2, "page_number": 4}, 0),
        (f"{settings.fast_api_dsn}/api/v1/films/search/", {"query": "testunknownmovie"}, 0),
        (f"{settings.fast_api_dsn}/api/v1/persons/search/", {"query": "Kunttu"}, 2),
        (f"{settings.fast_api_dsn}/api/v1/persons/search/", {"query": "Kunttu", "page_size": 2, "page_number": 1}, 2),
        (f"{settings.fast_api_dsn}/api/v1/persons/search/", {"query": "Kunttu", "page_size": 2, "page_number": 2}, 0),
        (f"{settings.fast_api_dsn}/api/v1/persons/search/", {"query": "testunknownperson"}, 0),
    ],
)
@pytest.mark.asyncio
async def test_search(
    client: aiohttp.ClientSession,
    url: str,
    query_data: dict[str, str | int],
    expected_len: int,
) -> None:
    async with client.get(url, params=query_data) as response:
        got = await response.json()

    assert len(got) == expected_len


@pytest.mark.functional
@pytest.mark.parametrize(
    ("url", "query_data", "redis_key", "expected_len"),
    [
        (f"{settings.fast_api_dsn}/api/v1/films/search/", {"query": "Star"}, "movies:search_by:<Star>:50:1", 5),
        (
            f"{settings.fast_api_dsn}/api/v1/films/search/",
            {"query": "Star", "page_size": 2, "page_number": 1},
            "movies:search_by:<Star>:2:1",
            2,
        ),
        (
            f"{settings.fast_api_dsn}/api/v1/films/search/",
            {"query": "Star", "page_size": 2, "page_number": 2},
            "movies:search_by:<Star>:2:2",
            2,
        ),
        (f"{settings.fast_api_dsn}/api/v1/persons/search/", {"query": "Kunttu"}, "person:search_by:<Kunttu>:50:1", 2),
        (
            f"{settings.fast_api_dsn}/api/v1/persons/search/",
            {"query": "Kunttu", "page_size": 2, "page_number": 1},
            "person:search_by:<Kunttu>:2:1",
            2,
        ),
        (
            f"{settings.fast_api_dsn}/api/v1/persons/search/",
            {"query": "Kunttu", "page_size": 2, "page_number": 2},
            "person:search_by:<Kunttu>:2:2",
            0,
        ),
    ],
)
@pytest.mark.asyncio
async def test_search_redis(
    client: aiohttp.ClientSession,
    redis_client: Redis,
    url: str,
    query_data: dict[str, str | int],
    redis_key: str,
    expected_len: int,
) -> None:
    await redis_client.delete(redis_key)
    await client.get(url=url, params=query_data)

    got = await redis_client.get(redis_key)

    got_data = json.loads(got) if got is not None else None
    assert got is not None
    assert len(got_data) == expected_len
    await redis_client.delete(redis_key)
