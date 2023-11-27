from unittest.mock import AsyncMock, patch

import pytest
from elasticsearch import AsyncElasticsearch

from db.repositories.person_es_repository import PersonElasticsearchRepository
from models.models import LimitOffset, Person


@pytest.mark.asyncio
class TestPersonElasticsearchRepository:
    def find_person_from_index(self, es_index_persons: dict, name: str, limit: int = 1000, offset: int = 1) -> dict:
        need_persons = []
        for person in es_index_persons["hits"]["hits"]:
            if name.lower() in person["_source"]["name"].lower():
                need_persons.append(person)
        offset -= 1
        return {"hits": {"hits": need_persons[offset : limit + offset]}}  # noqa: E203

    @patch.object(AsyncElasticsearch, "search", new_callable=AsyncMock)
    async def test_search(self, mock_search: AsyncMock, es_index_persons: dict) -> None:
        mock_search.return_value = self.find_person_from_index(es_index_persons, name="thomas")
        repo = PersonElasticsearchRepository(client=AsyncElasticsearch("http://test:9200/"))

        got = await repo.search(query="thomas", limit_offset=LimitOffset(limit=1000, offset=1))

        assert len(got) == 2
        assert isinstance(got[0], Person) and isinstance(got[1], Person)

    @patch.object(AsyncElasticsearch, "search", new_callable=AsyncMock)
    async def test_search_empty_list(self, mock_search: AsyncMock, es_index_persons: dict) -> None:
        mock_search.return_value = self.find_person_from_index(es_index_persons, name="unknown person name")
        repo = PersonElasticsearchRepository(client=AsyncElasticsearch("http://test:9200/"))

        got = await repo.search(query="unknown person name", limit_offset=LimitOffset(limit=1000, offset=1))

        assert got == []

    @patch.object(AsyncElasticsearch, "search", new_callable=AsyncMock)
    async def test_search_limit_offset(self, mock_search: AsyncMock, es_index_persons: dict) -> None:
        mock_search.return_value = self.find_person_from_index(es_index_persons, name="thomas", offset=2)
        repo = PersonElasticsearchRepository(client=AsyncElasticsearch("http://test:9200/"))

        got = await repo.search(query="unknown person name", limit_offset=LimitOffset(limit=1000, offset=2))

        assert len(got) == 1
        assert isinstance(got[0], Person)
