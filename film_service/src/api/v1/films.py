from http import HTTPStatus
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse

from db.exceptions import MovieNotFoundException
from models.controller_exceptions import MovieNotFound
from models.models import LimitOffset, Movie, MovieInfo
from services.movie_service import MovieService, get_movie_service
from services.auth_service import security_jwt

router = APIRouter()


@router.get(
    path="/search/",
    response_model=list[Movie],
    response_model_by_alias=False,
    response_model_include={"uuid", "title", "imdb_rating"},
)
async def search(
    user: Annotated[dict, Depends(security_jwt)],
    limit_offset: Annotated[LimitOffset, Depends(LimitOffset)],
    query: str = Query(min_length=1, description="Название фильма"),
    movie_service: MovieService = Depends(get_movie_service),
) -> list[Movie]:
    """Поиск фильмов по названию"""
    return await movie_service.search_movies(query, limit_offset)


@router.get(
    "/{film_id}/",
    response_model=Movie,
    response_model_by_alias=False,
    responses={HTTPStatus.NOT_FOUND: {"model": MovieNotFound}},
)
async def film_details(
    user: Annotated[dict, Depends(security_jwt)],
    film_id: UUID,
    movie_service: MovieService = Depends(get_movie_service),
) -> Movie:
    """Получить информацию о фильме по UUID."""
    try:
        movie = await movie_service.get_movie_by_id(id_=film_id)
    except MovieNotFoundException as exc:
            return JSONResponse(status_code=HTTPStatus.NOT_FOUND, content={"detail": exc.detail})
    return movie


@router.get(
    path="",
    response_model=list[MovieInfo],
    response_model_by_alias=True,
)
async def films(
    user: Annotated[dict, Depends(security_jwt)],
    limit_offset: Annotated[LimitOffset, Depends(LimitOffset)],
    sort: str = Query(
        default="imdb_rating",
        regex=r"[+-]?(imdb_rating|id)",
        description="Сортировка по рейтингу (-imdb_rating = desc)",
    ),
    genre_uuid: UUID | None = Query(default=None, alias="genre", description="Идентификатор жанра"),
    movie_service: MovieService = Depends(get_movie_service),
) -> list[MovieInfo]:
    """Получить список популярных фильмов/фильмов в определенном жанре."""
    if genre_uuid is None:
        return await movie_service.find_movies(sort=sort, limit_offset=limit_offset)
    return await movie_service.find_movies_by_genre_uuid(genre_uuid=genre_uuid, sort=sort, limit_offset=limit_offset)
