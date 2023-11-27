from typing import Type
from uuid import UUID

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends

from db.elastic import get_elastic
from db.es_repository import ESRepository
from db.exceptions import GenreNotFoundException
from models.models import Genre, LimitOffset, SortField


class GenreElasticsearchRepository(ESRepository):
    @property
    def index_name(self) -> str:
        return "genres"

    @property
    def base_model(self) -> Type[Genre]:
        return Genre

    async def get_by_id(self, id_: UUID) -> Genre:
        try:
            genre_form_es = await self._client.get(index="genres", id=id_)
        except NotFoundError:
            raise GenreNotFoundException(f"Genre with id={id_} not found")

        return Genre(**genre_form_es["_source"])

    async def find_all(self, sort: str, limit_offset: LimitOffset) -> list[Genre]:
        return await self._request(
            query={"match_all": {}},
            sort=SortField(sort),
            limit_offset=limit_offset,
        )


async def get_genre_repository(elastic: AsyncElasticsearch = Depends(get_elastic)) -> GenreElasticsearchRepository:
    return GenreElasticsearchRepository(client=elastic)
