from typing import Type
from uuid import UUID

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends

from db.elastic import get_elastic
from db.es_repository import ESRepository
from db.exceptions import MovieNotFoundException
from models.models import LimitOffset, Movie, SortField


class MoviesElasticsearchRepository(ESRepository):
    @property
    def index_name(self) -> str:
        return "movies"

    @property
    def base_model(self) -> Type[Movie]:
        return Movie

    async def get_by_id(self, id_: UUID) -> Movie:
        """Получить movie по идентификатору

        Args:
            id_: идентификатор индекса movie в формате uuid4

        Raises:
            MovieNotFoundException: фильм не найден

        Returns:
            Movie: сущность фильма
        """
        try:
            movie_form_es = await self._client.get(index="movies", id=id_)
        except NotFoundError:
            raise MovieNotFoundException(f"Movie with id={id_} not found")

        return Movie(**movie_form_es["_source"])

    async def find_all(self, sort: str, limit_offset: LimitOffset) -> list[Movie]:
        return await self._request(
            query={"match_all": {}},
            sort=SortField(sort),
            limit_offset=limit_offset,
        )

    async def find_by_genre_id(self, uuid: UUID, sort: str, limit_offset: LimitOffset) -> list[Movie]:
        return await self._request(
            query={"nested": {"path": "genres", "query": {"match": {"genres.id": uuid}}}},
            sort=SortField(sort),
            limit_offset=limit_offset,
        )

    async def search(self, query: str, limit_offset: LimitOffset) -> list[Movie]:
        return await self._request(
            query={"match": {"title": {"query": query, "fuzziness": "auto"}}},
            limit_offset=limit_offset,
        )

    async def find_by_person_ids(
        self, person_ids: list[UUID], limit_offset=LimitOffset(page_size=1000, page_number=1)
    ) -> list[Movie]:
        return await self._request(
            query={
                "bool": {
                    "should": [
                        {
                            "nested": {
                                "path": "actors",
                                "query": {"terms": {"actors.id": person_ids}},
                            }
                        },
                        {
                            "nested": {
                                "path": "writers",
                                "query": {"terms": {"writers.id": person_ids}},
                            }
                        },
                        {
                            "nested": {
                                "path": "directors",
                                "query": {"terms": {"directors.id": person_ids}},
                            }
                        },
                    ],
                    "minimum_should_match": 1,
                }
            },
            limit_offset=limit_offset,
            sort=SortField(sort_field_string="-imdb_rating"),
        )


async def get_movie_repository(elastic: AsyncElasticsearch = Depends(get_elastic)) -> MoviesElasticsearchRepository:
    return MoviesElasticsearchRepository(client=elastic)
