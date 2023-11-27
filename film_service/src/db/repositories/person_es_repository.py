from typing import Type
from uuid import UUID

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends

from db.elastic import get_elastic
from db.es_repository import ESRepository
from db.exceptions import PersonNotFoundException
from models.models import LimitOffset, Person, SortField


class PersonElasticsearchRepository(ESRepository):
    @property
    def index_name(self) -> str:
        return "persons"

    @property
    def base_model(self) -> Type[Person]:
        return Person

    async def search(self, query: str, limit_offset: LimitOffset) -> list[Person]:
        return await self._request(
            query={"match": {"name": {"query": query, "fuzziness": "auto"}}},
            limit_offset=limit_offset,
        )

    async def find_all(self, sort: str, limit_offset: LimitOffset) -> list[Person]:
        return await self._request(
            query={"match_all": {}},
            sort=SortField(sort),
            limit_offset=limit_offset,
        )

    async def get_by_id(self, id_: UUID) -> Person:
        try:
            person_form_es = await self._client.get(index="persons", id=id_)
        except NotFoundError:
            raise PersonNotFoundException(f"Person with id={id_} not found")

        return Person(**person_form_es["_source"])


async def get_person_repository(elastic: AsyncElasticsearch = Depends(get_elastic)) -> PersonElasticsearchRepository:
    return PersonElasticsearchRepository(client=elastic)
