import logging
from functools import lru_cache
from uuid import UUID

from fastapi import Depends

from db.redis_repository import RedisRepository, get_redis_repo
from db.repositories.genre_es_repository import GenreElasticsearchRepository, get_genre_repository
from models.models import Genre, LimitOffset

logger = logging.getLogger(__name__)


class GenreService:
    def __init__(
        self,
        redis_repository: RedisRepository,
        genre_repository: GenreElasticsearchRepository,
    ) -> None:
        self._genre_repository = genre_repository
        self._redis_repo = redis_repository

    async def get_genre_by_id(self, id_: UUID) -> Genre:
        redis_key = f"genre::{id_}"
        if genre_from_cache := await self._redis_repo.get_object(redis_key, Genre):
            return genre_from_cache
        genre = await self._genre_repository.get_by_id(id_=id_)
        await self._redis_repo.load_object(redis_key, genre)

        return genre

    async def find_genres(self, sort: str, limit_offset: LimitOffset) -> list[Genre]:
        redis_key = f"genre:{sort}:{limit_offset.limit}:{limit_offset.offset}"
        if genres_from_cache := await self._redis_repo.get_objects(redis_key, Genre):
            return genres_from_cache
        genres = await self._genre_repository.find_all(sort=sort, limit_offset=limit_offset)
        await self._redis_repo.load_objects(redis_key, genres)
        return genres


@lru_cache()
def get_genre_service(
    redis: RedisRepository = Depends(get_redis_repo),
    genre_repository: GenreElasticsearchRepository = Depends(get_genre_repository),
) -> GenreService:
    return GenreService(redis_repository=redis, genre_repository=genre_repository)
