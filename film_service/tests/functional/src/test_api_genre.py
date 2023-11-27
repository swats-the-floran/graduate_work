import json
from http import HTTPStatus

import aiohttp
import pytest
from redis.asyncio import Redis

from tests.functional.settings import settings


@pytest.mark.functional
@pytest.mark.parametrize(
    ("query_data", "expected_code"),
    [
        ({}, HTTPStatus.OK),
        ({"sort": "name"}, HTTPStatus.OK),
        ({"sort": "id"}, HTTPStatus.OK),
        ({"sort": "-name"}, HTTPStatus.OK),
        ({"sort": "-id"}, HTTPStatus.OK),
        ({"sort": "+name"}, HTTPStatus.OK),
        ({"sort": "+id"}, HTTPStatus.OK),
        ({"page_size": 1, "page_number": 1}, HTTPStatus.OK),
        ({"sort": ""}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({"page_size": -1}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({"page_size": 0}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({"sort": "unknown_field"}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({"sort": "-unknown_field"}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({"page_size": 1, "page_number": -1}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({"page_size": 1, "page_number": 0}, HTTPStatus.UNPROCESSABLE_ENTITY),
    ],
)
@pytest.mark.asyncio
async def test_genres_validate(
    client: aiohttp.ClientSession,
    query_data: dict[str, str | int],
    expected_code: int,
) -> None:
    async with client.get(f"{settings.fast_api_dsn}/api/v1/genres", params=query_data) as response:
        got = response.status

    assert got == expected_code


@pytest.mark.functional
@pytest.mark.parametrize(
    ("query_data", "expected"),
    [
        (
            {"sort": "+name", "page_size": 2},
            [
                {"uuid": "6a0a479b-cfec-41ac-b520-41b2b007b611", "name": "Animation"},
                {"uuid": "5373d043-3f41-4ea8-9947-4b746c601bbd", "name": "Comedy"},
            ],
        ),
        (
            {"sort": "-name", "page_size": 2},
            [
                {"uuid": "0b105f87-e0a5-45dc-8ce7-f8632088f390", "name": "Western"},
                {"uuid": "a886d0ec-c3f3-4b16-b973-dedcf5bfa395", "name": "Short"},
            ],
        ),
        (
            {"sort": "name", "page_size": 2, "page_number": 5},
            [
                {"uuid": "0b105f87-e0a5-45dc-8ce7-f8632088f390", "name": "Western"},
            ],
        ),
        (
            {"sort": "+id", "page_size": 1},
            [{"uuid": "0b105f87-e0a5-45dc-8ce7-f8632088f390", "name": "Western"}],
        ),
        (
            {"sort": "-id", "page_size": 1},
            [{"uuid": "fb58fd7f-7afd-447f-b833-e51e45e2a778", "name": "Game-Show"}],
        ),
    ],
)
@pytest.mark.asyncio
async def test_genres(
    client: aiohttp.ClientSession,
    query_data: dict[str, str | int],
    expected: list[dict[str, str]],
) -> None:
    async with client.get(f"{settings.fast_api_dsn}/api/v1/genres", params=query_data) as response:
        got = await response.json()

    assert got == expected


@pytest.mark.functional
@pytest.mark.parametrize(
    ("query_data", "redis_key", "expected_cache"),
    [
        (
            {"sort": "+name", "page_size": 1},
            "genre:+name:1:1",
            ['{"id":"6a0a479b-cfec-41ac-b520-41b2b007b611","name":"Animation"}'],
        ),
        (
            {"sort": "-name", "page_size": 2},
            "genre:-name:2:1",
            [
                '{"id":"0b105f87-e0a5-45dc-8ce7-f8632088f390","name":"Western"}',
                '{"id":"a886d0ec-c3f3-4b16-b973-dedcf5bfa395","name":"Short"}',
            ],
        ),
        (
            {"sort": "name", "page_size": 2, "page_number": 5},
            "genre:name:2:5",
            ['{"id":"0b105f87-e0a5-45dc-8ce7-f8632088f390","name":"Western"}'],
        ),
    ],
)
@pytest.mark.asyncio
async def test_genres_from_redis(
    client: aiohttp.ClientSession,
    redis_client: Redis,
    query_data: dict[str, str | int],
    redis_key: str,
    expected_cache: list[str],
) -> None:
    await redis_client.delete(redis_key)
    await client.get(url=f"{settings.fast_api_dsn}/api/v1/genres", params=query_data)

    got = await redis_client.get(redis_key)

    assert json.loads(got) == expected_cache
    await redis_client.delete(redis_key)


@pytest.mark.functional
@pytest.mark.parametrize(
    ("genre_id", "expected_code"),
    [
        ("1", HTTPStatus.UNPROCESSABLE_ENTITY),
        (123, HTTPStatus.UNPROCESSABLE_ENTITY),
        ("fb58fd7f-7afd-447f-b833-e51e45e2a778", HTTPStatus.OK),
    ],
)
@pytest.mark.asyncio
async def test_genre_details_validate(
    client: aiohttp.ClientSession,
    genre_id: str | int,
    expected_code: int,
) -> None:
    async with client.get(f"{settings.fast_api_dsn}/api/v1/genres/{genre_id}/") as response:
        got = response.status

    assert got == expected_code


@pytest.mark.functional
@pytest.mark.parametrize(
    ("genre_id", "expected"),
    [
        (
            "fb58fd7f-7afd-447f-b833-e51e45e2a778",
            {"uuid": "fb58fd7f-7afd-447f-b833-e51e45e2a778", "name": "Game-Show"},
        ),
    ],
)
@pytest.mark.asyncio
async def test_genre_details(
    client: aiohttp.ClientSession,
    genre_id: str,
    expected: dict[str, str],
) -> None:
    async with client.get(f"{settings.fast_api_dsn}/api/v1/genres/{genre_id}/") as response:
        got = await response.json()

    assert got == expected


@pytest.mark.functional
@pytest.mark.parametrize(
    ("genre_id", "expected"),
    [
        (
            "00000000-0000-0000-0000-000000000000",
            {"detail": "Genre with id=00000000-0000-0000-0000-000000000000 not found"},
        ),
    ],
)
@pytest.mark.asyncio
async def test_genre_details_unknown_genre(
    client: aiohttp.ClientSession,
    genre_id: str,
    expected: dict[str, str],
) -> None:
    async with client.get(f"{settings.fast_api_dsn}/api/v1/genres/{genre_id}/") as response:
        got = await response.json()
        got_status = response.status

    assert got_status == HTTPStatus.NOT_FOUND
    assert got == expected


@pytest.mark.functional
@pytest.mark.parametrize(
    ("genre_id", "redis_key", "expected_cache"),
    [
        (
            "fb58fd7f-7afd-447f-b833-e51e45e2a778",
            "genre::fb58fd7f-7afd-447f-b833-e51e45e2a778",
            {"id": "fb58fd7f-7afd-447f-b833-e51e45e2a778", "name": "Game-Show"},
        ),
    ],
)
@pytest.mark.asyncio
async def test_genre_details_from_redis(
    client: aiohttp.ClientSession,
    redis_client: Redis,
    genre_id: str,
    redis_key: str,
    expected_cache: dict[str, str],
) -> None:
    await redis_client.delete(redis_key)
    await client.get(f"{settings.fast_api_dsn}/api/v1/genres/{genre_id}/")

    got = await redis_client.get(redis_key)

    assert json.loads(got) == expected_cache
    await redis_client.delete(redis_key)
