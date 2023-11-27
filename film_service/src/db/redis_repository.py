import json
import logging
from typing import Type

from fastapi import Depends
from pydantic import BaseModel
from redis.asyncio import Redis

from core.config import settings
from db.redis import get_redis

logger = logging.getLogger(__name__)


class RedisRepository:
    def __init__(self, client: Redis):
        self._client = client

    async def get_object(self, key: str, mapper: Type[BaseModel]) -> BaseModel:
        if data_from_cache := await self._client.get(key):
            logger.info("<Get response from Redis for request - %s>", key)
            return mapper.parse_raw(data_from_cache)
        return None

    async def get_objects(self, key: str, mapper: Type[BaseModel]) -> list[BaseModel]:
        if data_from_cache := await self._client.get(key):
            logger.info("<Get response from Redis for request - %s>", key)
            return [mapper.parse_raw(genre_from_cache) for genre_from_cache in json.loads(data_from_cache)]
        return []

    async def load_object(self, key: str, row: BaseModel) -> None:
        await self._client.set(key, row.json(by_alias=True), ex=settings.redis.cache_expire)

    async def load_objects(self, key: str, rows: list[BaseModel]) -> None:
        objects_for_redis = [row.json(by_alias=True) for row in rows]
        await self._client.set(key, json.dumps(objects_for_redis), ex=settings.redis.cache_expire)


async def get_redis_repo(redis: Redis = Depends(get_redis)) -> RedisRepository:
    return RedisRepository(client=redis)
