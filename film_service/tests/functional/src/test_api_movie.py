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
        ({"sort": "imdb_rating"}, HTTPStatus.OK),
        ({"sort": "-imdb_rating"}, HTTPStatus.OK),
        ({"sort": "+imdb_rating"}, HTTPStatus.OK),
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
        ({"genre": ""}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({"genre": "6a0a479b-cfec-41ac-b520-41b2b007b611"}, HTTPStatus.OK),
        ({"genre": "00000000-0000-0000-0000-000000000000"}, HTTPStatus.OK),
        ({"genre": "1"}, HTTPStatus.UNPROCESSABLE_ENTITY),
    ],
)
@pytest.mark.asyncio
async def test_films_validate(
    client: aiohttp.ClientSession,
    query_data: dict[str, str | int],
    expected_code: int,
) -> None:
    async with client.get(f"{settings.fast_api_dsn}/api/v1/films", params=query_data) as response:
        got = response.status

    assert got == expected_code


@pytest.mark.functional
@pytest.mark.parametrize(
    ("query_data", "expected"),
    [
        (
            {"sort": "+imdb_rating", "page_size": 2},
            [
                {"id": "c516192c-fa26-431f-bb42-4fb6c6075998", "title": "To Be a Star", "imdb_rating": 6.1},
                {"id": "a010b701-9a46-4a23-aa5d-b029c18353dd", "title": "Big Star's Little Star", "imdb_rating": 6.3},
            ],
        ),
        (
            {"sort": "-imdb_rating", "page_size": 3},
            [
                {"id": "4df8c0cb-2cbf-4e40-b79c-fb07635775b9", "title": "Star Shaped Scar", "imdb_rating": 8},
                {"id": "ce98c597-42ed-4a60-af20-ec6f985d2ea2", "title": "Star", "imdb_rating": 7},
                {"id": "b164fef5-0867-46d8-b635-737e1721f6bf", "title": "Tar with a Star", "imdb_rating": 6.7},
            ],
        ),
        (
            {"sort": "imdb_rating", "page_size": 2, "page_number": 2},
            [
                {"id": "b164fef5-0867-46d8-b635-737e1721f6bf", "title": "Tar with a Star", "imdb_rating": 6.7},
                {"id": "ce98c597-42ed-4a60-af20-ec6f985d2ea2", "title": "Star", "imdb_rating": 7},
            ],
        ),
        (
            {"genre": "6a0a479b-cfec-41ac-b520-41b2b007b611"},
            [{"id": "b164fef5-0867-46d8-b635-737e1721f6bf", "title": "Tar with a Star", "imdb_rating": 6.7}],
        ),
        (
            {"sort": "id", "page_size": 3},
            [
                {"id": "4df8c0cb-2cbf-4e40-b79c-fb07635775b9", "title": "Star Shaped Scar", "imdb_rating": 8},
                {"id": "a010b701-9a46-4a23-aa5d-b029c18353dd", "title": "Big Star's Little Star", "imdb_rating": 6.3},
                {"id": "b164fef5-0867-46d8-b635-737e1721f6bf", "title": "Tar with a Star", "imdb_rating": 6.7},
            ],
        ),
        (
            {"sort": "+id", "page_size": 3},
            [
                {"id": "4df8c0cb-2cbf-4e40-b79c-fb07635775b9", "title": "Star Shaped Scar", "imdb_rating": 8},
                {"id": "a010b701-9a46-4a23-aa5d-b029c18353dd", "title": "Big Star's Little Star", "imdb_rating": 6.3},
                {"id": "b164fef5-0867-46d8-b635-737e1721f6bf", "title": "Tar with a Star", "imdb_rating": 6.7},
            ],
        ),
        (
            {"sort": "-id", "page_size": 3},
            [
                {"id": "ce98c597-42ed-4a60-af20-ec6f985d2ea2", "title": "Star", "imdb_rating": 7},
                {"id": "c516192c-fa26-431f-bb42-4fb6c6075998", "title": "To Be a Star", "imdb_rating": 6.1},
                {"id": "b164fef5-0867-46d8-b635-737e1721f6bf", "title": "Tar with a Star", "imdb_rating": 6.7},
            ],
        ),
    ],
)
@pytest.mark.asyncio
async def test_films(
    client: aiohttp.ClientSession,
    query_data: dict[str, str | int],
    expected: list[dict[str, str | float]],
) -> None:
    async with client.get(f"{settings.fast_api_dsn}/api/v1/films", params=query_data) as response:
        got = await response.json()

    assert got == expected


@pytest.mark.functional
@pytest.mark.parametrize(
    ("query_data", "redis_key", "expected_cache"),
    [
        (
            {"sort": "+imdb_rating", "page_size": 2},
            "movies:+imdb_rating:2:1",
            [
                '{"id":"c516192c-fa26-431f-bb42-4fb6c6075998","title":"To Be a Star","imdb_rating":6.1}',
                '{"id":"a010b701-9a46-4a23-aa5d-b029c18353dd","title":"Big Star\'s Little Star","imdb_rating":6.3}',
            ],
        ),
        (
            {"sort": "-imdb_rating", "page_size": 3},
            "movies:-imdb_rating:3:1",
            [
                '{"id":"4df8c0cb-2cbf-4e40-b79c-fb07635775b9","title":"Star Shaped Scar","imdb_rating":8.0}',
                '{"id":"ce98c597-42ed-4a60-af20-ec6f985d2ea2","title":"Star","imdb_rating":7.0}',
                '{"id":"b164fef5-0867-46d8-b635-737e1721f6bf","title":"Tar with a Star","imdb_rating":6.7}',
            ],
        ),
        (
            {"sort": "imdb_rating", "page_size": 2, "page_number": 2},
            "movies:imdb_rating:2:2",
            [
                '{"id":"b164fef5-0867-46d8-b635-737e1721f6bf","title":"Tar with a Star","imdb_rating":6.7}',
                '{"id":"ce98c597-42ed-4a60-af20-ec6f985d2ea2","title":"Star","imdb_rating":7.0}',
            ],
        ),
        (
            {"genre": "6a0a479b-cfec-41ac-b520-41b2b007b611"},
            "movies:genre_id:<6a0a479b-cfec-41ac-b520-41b2b007b611>:imdb_rating:50:1",
            ['{"id":"b164fef5-0867-46d8-b635-737e1721f6bf","title":"Tar with a Star","imdb_rating":6.7}'],
        ),
    ],
)
@pytest.mark.asyncio
async def test_films_from_redis(
    client: aiohttp.ClientSession,
    redis_client: Redis,
    query_data: dict[str, str | int],
    redis_key: str,
    expected_cache: list[str],
) -> None:
    await redis_client.delete(redis_key)
    await client.get(url=f"{settings.fast_api_dsn}/api/v1/films", params=query_data)

    got = await redis_client.get(redis_key)

    assert json.loads(got) == expected_cache
    await redis_client.delete(redis_key)


@pytest.mark.functional
@pytest.mark.parametrize(
    ("film_id", "expected_code"),
    [
        ("1", HTTPStatus.UNPROCESSABLE_ENTITY),
        (123, HTTPStatus.UNPROCESSABLE_ENTITY),
        ("ce98c597-42ed-4a60-af20-ec6f985d2ea2", HTTPStatus.OK),
    ],
)
@pytest.mark.asyncio
async def test_films_details_validate(
    client: aiohttp.ClientSession,
    film_id: str | int,
    expected_code: int,
) -> None:
    async with client.get(f"{settings.fast_api_dsn}/api/v1/films/{film_id}/") as response:
        got = response.status

    assert got == expected_code


@pytest.mark.functional
@pytest.mark.parametrize(
    ("film_id", "expected"),
    [
        (
            "ce98c597-42ed-4a60-af20-ec6f985d2ea2",
            {
                "uuid": "ce98c597-42ed-4a60-af20-ec6f985d2ea2",
                "title": "Star",
                "description": "Bradley is a huge movie star who still attends school. His star status conflicts with "
                "his envious teachers and his peers.",
                "imdb_rating": 7,
                "genres": [
                    {"uuid": "5373d043-3f41-4ea8-9947-4b746c601bbd", "name": "Comedy"},
                    {"uuid": "55c723c1-6d90-4a04-a44b-e9792040251a", "name": "Family"},
                ],
                "actors": [
                    {"id": "2dfcc75b-24b2-407e-bec8-a3d1d9fdb1fd", "full_name": "Liam Darbon"},
                    {"id": "aa486390-de5d-4988-87f4-cc867539af0b", "full_name": "Sasha Jackson"},
                    {"id": "dbdf8a38-6e59-4c83-bee6-99679cf19ca2", "full_name": "Tony Graimes"},
                    {"id": "fcfe6f65-846f-4fc7-b034-7a9237956b7b", "full_name": "Matthew Leitch"},
                ],
                "writers": [],
                "directors": [],
            },
        ),
    ],
)
@pytest.mark.asyncio
async def test_film_details(
    client: aiohttp.ClientSession,
    film_id: str,
    expected: dict[str, Any],
) -> None:
    async with client.get(f"{settings.fast_api_dsn}/api/v1/films/{film_id}/") as response:
        got = await response.json()

    assert got == expected


@pytest.mark.functional
@pytest.mark.parametrize(
    ("film_id", "expected"),
    [
        (
            "00000000-0000-0000-0000-000000000000",
            {"detail": "Movie with id=00000000-0000-0000-0000-000000000000 not found"},
        ),
    ],
)
@pytest.mark.asyncio
async def test_film_details_unknown_film(
    client: aiohttp.ClientSession,
    film_id: str,
    expected: dict[str, str],
) -> None:
    async with client.get(f"{settings.fast_api_dsn}/api/v1/films/{film_id}/") as response:
        got = await response.json()
        got_status = response.status

    assert got_status == HTTPStatus.NOT_FOUND
    assert got == expected


@pytest.mark.functional
@pytest.mark.parametrize(
    ("film_id", "redis_key", "expected_cache"),
    [
        (
            "ce98c597-42ed-4a60-af20-ec6f985d2ea2",
            "movie::ce98c597-42ed-4a60-af20-ec6f985d2ea2",
            {
                "id": "ce98c597-42ed-4a60-af20-ec6f985d2ea2",
                "title": "Star",
                "description": "Bradley is a huge movie star who still attends school. His star status conflicts with "
                "his envious teachers and his peers.",
                "imdb_rating": 7.0,
                "genres": [
                    {"id": "5373d043-3f41-4ea8-9947-4b746c601bbd", "name": "Comedy"},
                    {"id": "55c723c1-6d90-4a04-a44b-e9792040251a", "name": "Family"},
                ],
                "actors": [
                    {"id": "2dfcc75b-24b2-407e-bec8-a3d1d9fdb1fd", "name": "Liam Darbon"},
                    {"id": "aa486390-de5d-4988-87f4-cc867539af0b", "name": "Sasha Jackson"},
                    {"id": "dbdf8a38-6e59-4c83-bee6-99679cf19ca2", "name": "Tony Graimes"},
                    {"id": "fcfe6f65-846f-4fc7-b034-7a9237956b7b", "name": "Matthew Leitch"},
                ],
                "writers": [],
                "directors": [],
            },
        ),
    ],
)
@pytest.mark.asyncio
async def test_film_details_from_redis(
    client: aiohttp.ClientSession,
    redis_client: Redis,
    film_id: str,
    redis_key: str,
    expected_cache: dict[str, Any],
) -> None:
    await redis_client.delete(redis_key)
    await client.get(f"{settings.fast_api_dsn}/api/v1/films/{film_id}/")

    got = await redis_client.get(redis_key)

    assert json.loads(got) == expected_cache
    await redis_client.delete(redis_key)
