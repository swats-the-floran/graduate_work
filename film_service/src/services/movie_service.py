import logging
from functools import lru_cache
from uuid import UUID

from fastapi import Depends

from db.redis_repository import RedisRepository, get_redis_repo
from db.repositories.movie_es_repository import MoviesElasticsearchRepository, get_movie_repository
from models.models import LimitOffset, Movie, MovieInfo

logger = logging.getLogger(__name__)


class MovieService:
    def __init__(
        self,
        redis_repository: RedisRepository,
        movie_repository: MoviesElasticsearchRepository,
    ) -> None:
        self._movie_repository = movie_repository
        self._redis_repo = redis_repository

    async def get_movie_by_id(self, id_: UUID) -> Movie:
        """Получить фильм по идентификатору

        Args:
            id_: идентификатор фильма

        Returns:
            Movie: сущность фильма
        """
        redis_key = f"movie::{id_}"
        if movie_from_cache := await self._redis_repo.get_object(redis_key, Movie):
            return movie_from_cache
        movie = await self._movie_repository.get_by_id(id_=id_)
        await self._redis_repo.load_object(redis_key, movie)
        return movie

    async def find_movies(self, sort: str, limit_offset: LimitOffset) -> list[MovieInfo]:
        """Получить фильмы

        Args:
            sort: операция и поле по которому нужно сортировать.
                Пример: -imdb_rating (desc imdb_rating). Или ничего.
            limit: какое количество записей необходимо выбрать
            offset: какая "страница"

        Returns:
            list[Movie]: список сущностей Movie
        """
        redis_key = f"movies:{sort}:{limit_offset.limit}:{limit_offset.offset}"
        if movies_from_cache := await self._redis_repo.get_objects(redis_key, MovieInfo):
            return movies_from_cache
        movies = await self._movie_repository.find_all(sort=sort, limit_offset=limit_offset)
        movies_info = self._get_film_info(movies)
        await self._redis_repo.load_objects(redis_key, movies_info)
        return movies_info

    async def find_movies_by_genre_uuid(
        self, genre_uuid: UUID, sort: str, limit_offset: LimitOffset
    ) -> list[MovieInfo]:
        redis_key = f"movies:genre_id:<{genre_uuid}>:{sort}:{limit_offset.limit}:{limit_offset.offset}"
        if movies_from_cache := await self._redis_repo.get_objects(redis_key, MovieInfo):
            return movies_from_cache
        movies = await self._movie_repository.find_by_genre_id(uuid=genre_uuid, sort=sort, limit_offset=limit_offset)
        movies_info = self._get_film_info(movies)
        await self._redis_repo.load_objects(redis_key, movies_info)
        return movies_info

    async def search_movies(self, query: str, limit_offset: LimitOffset) -> list[Movie]:
        redis_key = f"movies:search_by:<{query}>:{limit_offset.limit}:{limit_offset.offset}"
        if movies_from_cache := await self._redis_repo.get_objects(redis_key, Movie):
            return movies_from_cache
        movies = await self._movie_repository.search(query=query, limit_offset=limit_offset)
        await self._redis_repo.load_objects(redis_key, movies)
        return movies

    @staticmethod
    def _get_film_info(movies: list[Movie]) -> list[MovieInfo]:
        return [
            MovieInfo(
                id=movie.uuid,
                title=movie.title,
                imdb_rating=movie.imdb_rating,
            )
            for movie in movies
        ]


@lru_cache()
def get_movie_service(
    redis: RedisRepository = Depends(get_redis_repo),
    movie_repository: MoviesElasticsearchRepository = Depends(get_movie_repository),
) -> MovieService:
    return MovieService(redis_repository=redis, movie_repository=movie_repository)
