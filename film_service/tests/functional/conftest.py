import json
from typing import Any

import aiohttp
import pytest
import pytest_asyncio
from elasticsearch import Elasticsearch
from redis.asyncio import Redis

from .settings import settings
from .testdata.es_settings import ES_DATA, INDEXES, SETTINGS, IndexName


@pytest_asyncio.fixture()
async def client() -> aiohttp.ClientSession:
    async with aiohttp.ClientSession() as client:
        yield client


@pytest_asyncio.fixture()
async def redis_client() -> Redis:
    async with Redis(host=settings.redis_host, port=settings.redis_port) as redis:
        yield redis


@pytest.fixture(scope="session", autouse=True)
def es_write_data() -> None:
    with Elasticsearch(hosts=settings.elastic_dsn) as client:
        for name, map_ in INDEXES.items():
            if client.indices.exists(index=name):
                continue
            _ = client.indices.create(index=name, settings=SETTINGS, mappings=map_)

        response = client.bulk(operations=request_es_query(es_data=ES_DATA), refresh=True)
        if response["errors"]:
            raise Exception("Ошибка записи данных в Elasticsearch")


def request_es_query(es_data: dict[IndexName, list[dict[str, Any]]]) -> str:
    bulk_query = []
    for index, data in es_data.items():
        for row in data:
            bulk_query.extend([json.dumps({"index": {"_index": index, "_id": row["id"]}}), json.dumps(row)])
    return "\n".join(bulk_query) + "\n"
