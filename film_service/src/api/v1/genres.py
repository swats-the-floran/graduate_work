from http import HTTPStatus
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse

from db.exceptions import GenreNotFoundException
from models.controller_exceptions import GenreNotFound
from models.models import Genre, LimitOffset
from services.genre_service import GenreService, get_genre_service
from services.auth_service import security_jwt

router = APIRouter()


@router.get(
    "/{genre_id}/",
    response_model=Genre,
    response_model_by_alias=False,
    responses={HTTPStatus.NOT_FOUND: {"model": GenreNotFound}},
)
async def genre_details(
    user: Annotated[dict, Depends(security_jwt)],
    genre_id: UUID,
    genre_service: GenreService = Depends(get_genre_service)
) -> Genre:
    """Получить информацию о жанре"""
    try:
        genre = await genre_service.get_genre_by_id(id_=genre_id)
    except GenreNotFoundException as exc:
        return JSONResponse(status_code=HTTPStatus.NOT_FOUND, content={"detail": exc.detail})
    return genre


@router.get(
    path="",
    response_model=list[Genre],
    response_model_by_alias=False,
    response_model_include={"uuid", "name"},
)
async def genres(
    user: Annotated[dict, Depends(security_jwt)],
    limit_offset: Annotated[LimitOffset, Depends(LimitOffset)],
    sort: str = Query(
        default="name",
        regex=r"[+-]?(name|id)",
    ),
    genre_service: GenreService = Depends(get_genre_service),
) -> list[Genre]:
    """Получить списко всех жанров"""
    return await genre_service.find_genres(sort=sort, limit_offset=limit_offset)
