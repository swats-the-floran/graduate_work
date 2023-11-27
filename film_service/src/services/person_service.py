import logging
from collections import defaultdict
from functools import lru_cache
from uuid import UUID

from fastapi import Depends

from db.es_repository import ESRepository
from db.redis_repository import RedisRepository, get_redis_repo
from db.repositories.movie_es_repository import MoviesElasticsearchRepository, get_movie_repository
from db.repositories.person_es_repository import PersonElasticsearchRepository, get_person_repository
from models.models import LimitOffset, Movie, MovieInfo, Person, PersonInfo, Role

logger = logging.getLogger(__name__)


class PersonService:
    def __init__(
        self,
        redis_repository: RedisRepository,
        person_repository: PersonElasticsearchRepository,
        movie_repository: MoviesElasticsearchRepository,
    ) -> None:
        self._movie_repository = movie_repository
        self._person_repository = person_repository
        self._redis_repo = redis_repository

    async def search_persons(self, query: str, limit_offset: LimitOffset) -> list[PersonInfo]:
        redis_key = f"person:search_by:<{query}>:{limit_offset.limit}:{limit_offset.offset}"
        if persons_from_cache := await self._redis_repo.get_objects(redis_key, PersonInfo):
            return persons_from_cache
        persons: list[Person] = await self._person_repository.search(query=query, limit_offset=limit_offset)
        movies: list[Movie] = await self._movie_repository.find_by_person_ids([person.id for person in persons])
        person_films = self._get_person_films(movies)
        persons_info = self._get_persons_info(person_films, persons)
        await self._redis_repo.load_objects(redis_key, persons_info)
        return persons_info

    async def find_movies_by_person_uuid(self, person_uuid: UUID, limit_offset: LimitOffset) -> list[MovieInfo]:
        redis_key = f"person:<{person_uuid}>:movies:{limit_offset.limit}:{limit_offset.offset}"
        if movies_from_cache := await self._redis_repo.get_objects(redis_key, MovieInfo):
            return movies_from_cache
        movies = await self._movie_repository.find_by_person_ids([person_uuid], limit_offset)
        movies_info = self._get_film_info(movies)
        await self._redis_repo.load_objects(redis_key, movies_info)
        return movies

    async def get_person_by_id(self, id_: UUID) -> PersonInfo:
        redis_key = f"person:::{id_}"
        if person_from_cache := await self._redis_repo.get_object(redis_key, PersonInfo):
            return person_from_cache
        person: Person = await self._person_repository.get_by_id(id_=id_)
        movies: list[Movie] = await self._movie_repository.find_by_person_ids([person.id])
        person_films = self._get_person_films(movies)
        person_info = self._get_persons_info(person_films, [person])[0]
        await self._redis_repo.load_object(redis_key, person_info)
        return person_info

    async def find_persons(self, sort: str, limit_offset: LimitOffset) -> list[Person]:
        redis_key = f"persons:{sort}:{limit_offset.limit}:{limit_offset.offset}"
        if persons_from_cache := await self._redis_repo.get_objects(redis_key, Person):
            return persons_from_cache
        persons: list[Person] = await self._person_repository.find_all(sort=sort, limit_offset=limit_offset)
        await self._redis_repo.load_objects(redis_key, persons)
        return persons

    @staticmethod
    def _get_persons_info(person_films: defaultdict, persons: list[Person]) -> list[PersonInfo]:
        return [
            PersonInfo(
                uuid=person.id,
                full_name=person.full_name,
                films=[{"uuid": key, "roles": value} for key, value in person_films[person.id]["films"].items()],
            )
            for person in persons
        ]

    @staticmethod
    def _get_person_films(movies: list[Movie]):
        person_films = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        for movie in movies:
            for actor in movie.actors:
                person_films[actor.id]["films"][movie.uuid].append(Role.ACTOR)
            for writer in movie.writers:
                person_films[writer.id]["films"][movie.uuid].append(Role.WRITER)
            for director in movie.directors:
                person_films[director.id]["films"][movie.uuid].append(Role.DIRECTOR)
        return person_films

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
def get_person_service(
    redis: RedisRepository = Depends(get_redis_repo),
    person_repository: ESRepository = Depends(get_person_repository),
    movie_repository: ESRepository = Depends(get_movie_repository),
) -> PersonService:
    return PersonService(redis_repository=redis, person_repository=person_repository, movie_repository=movie_repository)
