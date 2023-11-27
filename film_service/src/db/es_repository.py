import abc
from typing import Any, Type

from elasticsearch import AsyncElasticsearch

from models.models import Genre, LimitOffset, Movie, Person, SortField


class ESRepository(abc.ABC):
    def __init__(self, client: AsyncElasticsearch):
        self._client = client

    @property
    @abc.abstractmethod
    def index_name(self) -> str:
        pass

    @property
    @abc.abstractmethod
    def base_model(self) -> Type[Movie] | Type[Person]:
        pass

    async def _request(
        self,
        query: dict[str, Any],
        limit_offset: LimitOffset,
        sort: SortField | None = None,
    ) -> list[Movie] | list[Person] | list[Genre]:
        data = await self._client.search(
            index=self.index_name,
            query=query,
            size=limit_offset.limit,
            from_=(limit_offset.offset - 1) * limit_offset.limit,
            sort=[{sort.field: {"order": sort.operation}}] if sort else None,
        )
        return [self.base_model(**model_data["_source"]) for model_data in data["hits"]["hits"]]
