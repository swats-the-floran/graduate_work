import json
from http import HTTPStatus
from typing import Any

import aiohttp
import pytest
from redis.asyncio import Redis

from tests.functional.settings import settings


@pytest.mark.functional
@pytest.mark.parametrize(
    ("query_data", "expected_code"),
    [
        ({}, HTTPStatus.OK),
        ({"sort": "id"}, HTTPStatus.OK),
        ({"sort": "-id"}, HTTPStatus.OK),
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
async def test_persons_validate(
    client: aiohttp.ClientSession,
    query_data: dict[str, str | int],
    expected_code: int,
) -> None:
    async with client.get(f"{settings.fast_api_dsn}/api/v1/persons", params=query_data) as response:
        got = response.status

    assert got == expected_code


@pytest.mark.functional
@pytest.mark.parametrize(
    ("query_data", "expected"),
    [
        (
            {"sort": "+id", "page_size": 2},
            [
                {"id": "0d7379fb-3013-4f24-a45b-aa1954c55a8f", "name": "Haim Idisis"},
                {"id": "2cd4f104-b13d-4ea7-9855-e5657eb177d6", "name": "Virva Kunttu"},
            ],
        ),
        (
            {"sort": "-id", "page_size": 2},
            [
                {"id": "fcfe6f65-846f-4fc7-b034-7a9237956b7b", "name": "Matthew Leitch"},
                {"id": "dbdf8a38-6e59-4c83-bee6-99679cf19ca2", "name": "Tony Graimes"},
            ],
        ),
        (
            {"sort": "id", "page_size": 2, "page_number": 5},
            [
                {"id": "5fc24d3d-fa60-4477-ab50-9c1d6abbefee", "name": "Arnon Zadok"},
                {"id": "67503a36-dc38-4104-abfe-3cea92db2e89", "name": "Chaim Elmakias"},
            ],
        ),
    ],
)
@pytest.mark.asyncio
async def test_persons(
    client: aiohttp.ClientSession,
    query_data: dict[str, str | int],
    expected: list[dict[str, str]],
) -> None:
    async with client.get(f"{settings.fast_api_dsn}/api/v1/persons", params=query_data) as response:
        got = await response.json()

    assert got == expected


@pytest.mark.functional
@pytest.mark.parametrize(
    ("query_data", "redis_key", "expected_cache"),
    [
        (
            {"sort": "+id", "page_size": 1},
            "persons:+id:1:1",
            ['{"id":"0d7379fb-3013-4f24-a45b-aa1954c55a8f","name":"Haim Idisis"}'],
        ),
        (
            {"sort": "-id", "page_size": 2},
            "persons:-id:2:1",
            [
                '{"id":"fcfe6f65-846f-4fc7-b034-7a9237956b7b","name":"Matthew Leitch"}',
                '{"id":"dbdf8a38-6e59-4c83-bee6-99679cf19ca2","name":"Tony Graimes"}',
            ],
        ),
        (
            {"sort": "id", "page_size": 2, "page_number": 5},
            "persons:id:2:5",
            [
                '{"id":"5fc24d3d-fa60-4477-ab50-9c1d6abbefee","name":"Arnon Zadok"}',
                '{"id":"67503a36-dc38-4104-abfe-3cea92db2e89","name":"Chaim Elmakias"}',
            ],
        ),
    ],
)
@pytest.mark.asyncio
async def test_persons_from_redis(
    client: aiohttp.ClientSession,
    redis_client: Redis,
    query_data: dict[str, str | int],
    redis_key: str,
    expected_cache: list[str],
) -> None:
    await redis_client.delete(redis_key)
    await client.get(url=f"{settings.fast_api_dsn}/api/v1/persons", params=query_data)

    got = await redis_client.get(redis_key)

    assert json.loads(got) == expected_cache
    await redis_client.delete(redis_key)


@pytest.mark.functional
@pytest.mark.parametrize(
    ("person_id", "expected_code"),
    [
        ("1", HTTPStatus.UNPROCESSABLE_ENTITY),
        (123, HTTPStatus.UNPROCESSABLE_ENTITY),
        ("67503a36-dc38-4104-abfe-3cea92db2e89", HTTPStatus.OK),
        ("00000000-0000-0000-0000-000000000000", 404),
    ],
)
@pytest.mark.asyncio
async def test_persons_details_validate(
    client: aiohttp.ClientSession,
    person_id: str | int,
    expected_code: int,
) -> None:
    async with client.get(f"{settings.fast_api_dsn}/api/v1/persons/{person_id}/") as response:
        got = response.status

    assert got == expected_code


@pytest.mark.functional
@pytest.mark.parametrize(
    ("person_id", "expected"),
    [
        (
            "67503a36-dc38-4104-abfe-3cea92db2e89",
            {
                "uuid": "67503a36-dc38-4104-abfe-3cea92db2e89",
                "full_name": "Chaim Elmakias",
                "films": [{"uuid": "c516192c-fa26-431f-bb42-4fb6c6075998", "roles": ["actor"]}],
            },
        ),
    ],
)
@pytest.mark.asyncio
async def test_person_details(
    client: aiohttp.ClientSession,
    person_id: str,
    expected: dict[str, Any],
) -> None:
    async with client.get(f"{settings.fast_api_dsn}/api/v1/persons/{person_id}/") as response:
        got = await response.json()

    assert got == expected


@pytest.mark.functional
@pytest.mark.parametrize(
    ("person_id", "expected"),
    [
        (
            "00000000-0000-0000-0000-000000000000",
            {"detail": "Person with id=00000000-0000-0000-0000-000000000000 not found"},
        ),
    ],
)
@pytest.mark.asyncio
async def test_person_details_unknown_person(
    client: aiohttp.ClientSession,
    person_id: str,
    expected: dict[str, str],
) -> None:
    async with client.get(f"{settings.fast_api_dsn}/api/v1/persons/{person_id}/") as response:
        got = await response.json()
        got_expected = response.status

    assert got_expected == HTTPStatus.NOT_FOUND
    assert got == expected


@pytest.mark.functional
@pytest.mark.parametrize(
    ("person_id", "redis_key", "expected_cache"),
    [
        (
            "67503a36-dc38-4104-abfe-3cea92db2e89",
            "person:::67503a36-dc38-4104-abfe-3cea92db2e89",
            {
                "uuid": "67503a36-dc38-4104-abfe-3cea92db2e89",
                "full_name": "Chaim Elmakias",
                "films": [{"uuid": "c516192c-fa26-431f-bb42-4fb6c6075998", "roles": ["actor"]}],
            },
        ),
    ],
)
@pytest.mark.asyncio
async def test_person_details_from_redis(
    client: aiohttp.ClientSession,
    redis_client: Redis,
    person_id: str,
    redis_key: str,
    expected_cache: dict[str, Any],
) -> None:
    await redis_client.delete(redis_key)
    await client.get(f"{settings.fast_api_dsn}/api/v1/persons/{person_id}/")

    got = await redis_client.get(redis_key)

    assert json.loads(got) == expected_cache
    await redis_client.delete(redis_key)


@pytest.mark.functional
@pytest.mark.parametrize(
    ("person_id", "expected"),
    [
        (
            "67503a36-dc38-4104-abfe-3cea92db2e89",
            [{"id": "c516192c-fa26-431f-bb42-4fb6c6075998", "title": "To Be a Star", "imdb_rating": 6.1}],
        ),
        ("00000000-0000-0000-0000-000000000000", []),
    ],
)
@pytest.mark.asyncio
async def test_person_films(
    client: aiohttp.ClientSession,
    person_id: str,
    expected: list[dict[str, str | float]],
) -> None:
    async with client.get(f"{settings.fast_api_dsn}/api/v1/persons/{person_id}/film") as response:
        got = await response.json()

    assert got == expected


@pytest.mark.functional
@pytest.mark.parametrize(
    ("person_id", "query_data", "redis_key", "expected_cache"),
    [
        (
            "67503a36-dc38-4104-abfe-3cea92db2e89",
            {"page_size": 1, "page_number": 1},
            "person:<67503a36-dc38-4104-abfe-3cea92db2e89>:movies:1:1",
            ['{"id":"c516192c-fa26-431f-bb42-4fb6c6075998","title":"To Be a Star","imdb_rating":6.1}'],
        ),
    ],
)
@pytest.mark.asyncio
async def test_person_films_from_redis(
    client: aiohttp.ClientSession,
    redis_client: Redis,
    person_id: str,
    query_data: str,
    redis_key: str,
    expected_cache: list[str],
) -> None:
    await redis_client.delete(redis_key)
    await client.get(f"{settings.fast_api_dsn}/api/v1/persons/{person_id}/film", params=query_data)

    got = await redis_client.get(redis_key)

    assert json.loads(got) == expected_cache
    await redis_client.delete(redis_key)
