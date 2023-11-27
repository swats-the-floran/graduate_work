from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID

import pytest

from db.exceptions import MovieNotFoundException
from db.repositories.movie_es_repository import MoviesElasticsearchRepository
from models.models import LimitOffset, Movie
from services.movie_service import MovieService


@pytest.mark.asyncio
class TestMovieService:
    def setup_method(
        self,
    ) -> None:
        self.redis_client = AsyncMock()
        self.redis_client.set = AsyncMock(return_value=None)
        self.redis_client.get = AsyncMock(return_value=None)
        self.service = MovieService(
            redis_client=self.redis_client,
            movie_repository=MoviesElasticsearchRepository(client=AsyncMock()),
        )

    @patch.object(MoviesElasticsearchRepository, "get_by_id", new_callable=AsyncMock)
    async def test_get_movie_by_id(self, mock_get_by_id: AsyncMock, default_movie: Movie) -> None:
        mock_get_by_id.return_value = default_movie

        got = await self.service.get_movie_by_id(id_=UUID("3bdae84f-9a04-4b04-9f7c-c05582d529e5"))

        assert isinstance(got, Movie)
        self.redis_client.get.assert_called_once()
        self.redis_client.set.assert_called_once()

    @patch.object(MoviesElasticsearchRepository, "get_by_id", new_callable=AsyncMock)
    async def test_get_movie_by_id_raise(self, mock_get_by_id: AsyncMock) -> None:
        mock_get_by_id.side_effect = MovieNotFoundException(
            "Movie with id=00000000-0000-0000-0000-000000000000 not found"
        )

        with pytest.raises(MovieNotFoundException):
            await self.service.get_movie_by_id(id_=UUID("00000000-0000-0000-0000-000000000000"))

    @patch.object(MoviesElasticsearchRepository, "find_all", new_callable=AsyncMock)
    async def test_find_movies(self, mock_find: MagicMock, search_movies_fixture: list[Movie]) -> None:
        mock_find.return_value = search_movies_fixture

        got = await self.service.find_movies(
            sort="imdb_rating",
            limit_offset=LimitOffset(limit=50, offset=1),
        )

        assert len(got) == 2
        assert isinstance(got[0], Movie) and isinstance(got[1], Movie)
        self.redis_client.get.assert_called_once()
        self.redis_client.set.assert_called_once()

    @patch.object(MoviesElasticsearchRepository, "find_by_genre_id", new_callable=AsyncMock)
    async def test_find_movies_by_genre_uuid(
        self, mock_find: MagicMock, find_movies_by_genre_action: list[Movie]
    ) -> None:
        mock_find.return_value = find_movies_by_genre_action

        got = await self.service.find_movies_by_genre_uuid(
            genre_uuid="3d8d9bf5-0d90-4353-88ba-4ccc5d2c07ff",
            sort="imdb_rating",
            limit_offset=LimitOffset(limit=50, offset=1),
        )

        assert len(got) == 1
        assert isinstance(got[0], Movie)
        self.redis_client.get.assert_called_once()
        self.redis_client.set.assert_called_once()

    @patch.object(MoviesElasticsearchRepository, "search", new_callable=AsyncMock)
    async def test_search_movies(self, mock_search_movies: MagicMock, search_movies_fixture: list[Movie]) -> None:
        mock_search_movies.return_value = search_movies_fixture

        got = await self.service.search_movies(
            query="start",
            limit_offset=LimitOffset(limit=50, offset=1),
        )

        assert len(got) == 2
        assert isinstance(got[0], Movie) and isinstance(got[1], Movie)
        self.redis_client.get.assert_called_once()
        self.redis_client.set.assert_called_once()

    @patch.object(MoviesElasticsearchRepository, "search", new_callable=AsyncMock)
    async def test_search_movies_empty_list(self, mock_search_movies: MagicMock) -> None:
        mock_search_movies.return_value = []

        got = await self.service.search_movies(
            query="asldjalksdjlkajlsdlaksjd",
            limit_offset=LimitOffset(limit=50, offset=1),
        )

        assert got == []
        self.redis_client.get.assert_called_once()
        self.redis_client.set.assert_called_once()
