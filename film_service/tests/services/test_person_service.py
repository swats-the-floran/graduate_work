from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from elasticsearch import AsyncElasticsearch

from db.repositories.person_es_repository import PersonElasticsearchRepository
from models.models import LimitOffset, PersonInfo
from services.person_service import PersonService


@pytest.mark.asyncio
class TestMovieService:
    def find_person_from_index(self, es_index_persons: dict, name: str, limit: int = 1000, offset: int = 1) -> dict:
        need_persons = []
        for person in es_index_persons["hits"]["hits"]:
            if name.lower() in person["_source"]["name"].lower():
                need_persons.append(person)
        offset -= 1
        return {"hits": {"hits": need_persons[offset : limit + offset]}}  # noqa: E203

    def setup_method(self) -> None:
        self.redis_client = AsyncMock()
        self.redis_client.set = AsyncMock(return_value=None)
        self.redis_client.get = AsyncMock(return_value=None)
        self.service = PersonService(
            redis_client=self.redis_client,
            person_repository=PersonElasticsearchRepository(client=AsyncElasticsearch("http://test:9200/")),
            movie_repository=AsyncMock(),
        )

    @patch.object(AsyncElasticsearch, "search", new_callable=AsyncMock)
    async def test_search_person(self, mock_search: MagicMock, es_index_persons: dict) -> None:
        mock_search.return_value = self.find_person_from_index(es_index_persons, name="thomas")

        got = await self.service.search_persons(query="thomas", limit_offset=LimitOffset(limit=1000, offset=1))

        assert len(got) == 2
        assert isinstance(got[0], PersonInfo) and isinstance(got[1], PersonInfo)
        self.redis_client.get.assert_called_once()
        self.redis_client.set.assert_called_once()

    @patch.object(AsyncElasticsearch, "search", new_callable=AsyncMock)
    async def test_search_person_empty_list(self, mock_search: MagicMock, es_index_persons: dict) -> None:
        mock_search.return_value = self.find_person_from_index(es_index_persons, name="unknown person name")

        got = await self.service.search_persons(
            query="unknown person name", limit_offset=LimitOffset(limit=1000, offset=1)
        )

        assert got == []
        self.redis_client.get.assert_called_once()
        self.redis_client.set.assert_called_once()

    @patch.object(AsyncElasticsearch, "search", new_callable=AsyncMock)
    async def test_search_person_offset(self, mock_search: MagicMock, es_index_persons: dict) -> None:
        mock_search.return_value = self.find_person_from_index(es_index_persons, name="thomas", offset=2)

        got = await self.service.search_persons(
            query="unknown person name", limit_offset=LimitOffset(limit=1000, offset=2)
        )

        assert len(got) == 1
        assert isinstance(got[0], PersonInfo)
        self.redis_client.get.assert_called_once()
        self.redis_client.set.assert_called_once()
