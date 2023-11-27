from typing import Any
from unittest.mock import AsyncMock, patch
from uuid import UUID

import pytest
from elasticsearch import AsyncElasticsearch, NotFoundError

from db.exceptions import MovieNotFoundException
from db.repositories.movie_es_repository import MoviesElasticsearchRepository
from models.models import LimitOffset, Movie


@pytest.mark.asyncio
class TestMovieElasticsearchRepository:
    def setup_method(self) -> None:
        self.repo = MoviesElasticsearchRepository(client=AsyncElasticsearch("http://test:9200/"))

    def find_limit_offset(self, movies: dict, limit: int, offset: int) -> None:
        offset -= 1
        hits: list = movies["hits"]["hits"]
        movies["hits"]["hits"] = hits[offset : offset + limit]  # noqa: E203
        return movies

    @patch.object(AsyncElasticsearch, "get", new_callable=AsyncMock)
    async def test_get_by_id(
        self, mock_get: AsyncMock, es_index_movie_one: dict[str, Any], default_movie: Movie
    ) -> None:
        mock_get.return_value = es_index_movie_one

        got = await self.repo.get_by_id(id_=UUID("3bdae84f-9a04-4b04-9f7c-c05582d529e5"))

        assert got == default_movie

    @patch.object(AsyncElasticsearch, "get", new_callable=AsyncMock)
    async def test_get_by_id_raise_movie_not_found_exception(
        self, mock_get: AsyncMock, not_found_error_from_es: NotFoundError
    ) -> None:
        mock_get.side_effect = not_found_error_from_es

        with pytest.raises(MovieNotFoundException) as exc:
            await self.repo.get_by_id(id_=UUID("00000000-0000-0000-0000-000000000000"))

        assert "Movie with id=00000000-0000-0000-0000-000000000000 not found" in str(exc)

    @patch.object(AsyncElasticsearch, "search", new_callable=AsyncMock)
    async def test_find_all_with_sort_imdb_rating(
        self, mock_search: AsyncMock, desc_es_index_search_movies: dict
    ) -> None:
        mock_search.return_value = self.find_limit_offset(desc_es_index_search_movies, 10, 1)

        got = await self.repo.find_all(sort="-imdb_rating", limit_offset=LimitOffset(limit=10, offset=1))

        assert len(got) == 2
        assert isinstance(got[0], Movie) and isinstance(got[1], Movie)
        assert got[0].uuid == UUID("05d7341e-e367-4e2e-acf5-4652a8435f93")

    @patch.object(AsyncElasticsearch, "search", new_callable=AsyncMock)
    async def test_find_all_with_without_sort(self, mock_search: AsyncMock, es_index_search_movies: dict) -> None:
        mock_search.return_value = self.find_limit_offset(es_index_search_movies, 10, 1)

        got = await self.repo.find_all(sort="imdb_rating", limit_offset=LimitOffset(limit=10, offset=1))

        assert len(got) == 2
        assert isinstance(got[0], Movie) and isinstance(got[1], Movie)
        assert got[0].uuid == UUID("3bdae84f-9a04-4b04-9f7c-c05582d529e5")

    @patch.object(AsyncElasticsearch, "search", new_callable=AsyncMock)
    async def test_find_all_with_pagination(self, mock_search: AsyncMock, desc_es_index_search_movies: dict) -> None:
        mock_search.return_value = self.find_limit_offset(desc_es_index_search_movies, 2, 2)

        got = await self.repo.find_all(sort="imdb_rating", limit_offset=LimitOffset(limit=2, offset=2))

        assert len(got) == 1
        assert isinstance(got[0], Movie)
        assert got[0].uuid == UUID("3bdae84f-9a04-4b04-9f7c-c05582d529e5")

    @patch.object(AsyncElasticsearch, "search", new_callable=AsyncMock)
    async def test_find_by_genre_id_desc(self, mock_search: AsyncMock, desc_es_index_search_movies: dict) -> None:
        mock_search.return_value = self.find_limit_offset(desc_es_index_search_movies, 2, 2)

        got = await self.repo.find_by_genre_id(
            uuid=UUID("3d8d9bf5-0d90-4353-88ba-4ccc5d2c07ff"),
            sort="-imdb_rating",
            limit_offset=LimitOffset(limit=1000, offset=1),
        )

        assert len(got) == 1
        assert isinstance(got[0], Movie)
        assert got[0].uuid == UUID("3bdae84f-9a04-4b04-9f7c-c05582d529e5")

    @patch.object(AsyncElasticsearch, "search", new_callable=AsyncMock)
    async def test_find_by_genre_id_asc(self, mock_search: AsyncMock, desc_es_index_search_movies: dict) -> None:
        mock_search.return_value = self.find_limit_offset(desc_es_index_search_movies, 2, 2)

        got = await self.repo.find_by_genre_id(
            uuid=UUID("3d8d9bf5-0d90-4353-88ba-4ccc5d2c07ff"),
            sort="imdb_rating",
            limit_offset=LimitOffset(limit=1000, offset=1),
        )

        assert len(got) == 1
        assert isinstance(got[0], Movie)
        assert got[0].uuid == UUID("3bdae84f-9a04-4b04-9f7c-c05582d529e5")

    @patch.object(AsyncElasticsearch, "search", new_callable=AsyncMock)
    async def test_search(self, mock_search: AsyncMock, es_index_search_movies: dict) -> None:
        mock_search.return_value = es_index_search_movies
        got = await self.repo.search(query="star", limit_offset=LimitOffset(limit=1000, offset=1))

        assert len(got) == 2
        assert isinstance(got[0], Movie) and isinstance(got[1], Movie)
        assert "star" in got[0].title.lower() and "star" in got[1].title.lower()

    @patch.object(AsyncElasticsearch, "search", new_callable=AsyncMock)
    async def test_search_with_pagination(self, mock_search: AsyncMock, es_index_search_movies: dict) -> None:
        mock_search.return_value = self.find_limit_offset(es_index_search_movies, 2, 2)

        got = await self.repo.search(query="lksaoiauroiqwhalasdljlk", limit_offset=LimitOffset(limit=2, offset=2))

        assert len(got) == 1
        assert isinstance(got[0], Movie)
        assert "star" in got[0].title.lower()

    @patch.object(AsyncElasticsearch, "search", new_callable=AsyncMock)
    async def test_search_query_not_found_in_es(self, mock_search: AsyncMock) -> None:
        mock_search.return_value = {"hits": {"hits": []}}

        got = await self.repo.search(query="lksaoiauroiqwhalasdljlk", limit_offset=LimitOffset(limit=2, offset=2))

        assert got == []
