from http import HTTPStatus
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse

from db.exceptions import PersonNotFoundException
from models.controller_exceptions import PersonNotFound
from models.models import LimitOffset, MovieInfo, Person, PersonInfo
from services.person_service import PersonService, get_person_service
from services.auth_service import security_jwt

router = APIRouter()


@router.get(path="/search/")
async def search(
    user: Annotated[dict, Depends(security_jwt)],
    limit_offset: Annotated[LimitOffset, Depends(LimitOffset)],
    query: str = Query(min_length=1, description="ФИО персоны"),
    person_service: PersonService = Depends(get_person_service),
) -> list[PersonInfo]:
    """Поиск персон по ФИО"""
    return await person_service.search_persons(query, limit_offset)


@router.get(
    "/{person_id}/",
    response_model=PersonInfo,
    response_model_by_alias=False,
    responses={HTTPStatus.NOT_FOUND: {"model": PersonNotFound}},
)
async def person_details(
    user: Annotated[dict, Depends(security_jwt)],
    person_id: UUID,
    person_service: PersonService = Depends(get_person_service)
) -> PersonInfo:
    """Получить персону по идентификатору"""
    try:
        person = await person_service.get_person_by_id(id_=person_id)
    except PersonNotFoundException as exc:
        return JSONResponse(status_code=HTTPStatus.NOT_FOUND, content={"detail": exc.detail})
    return person


@router.get(
    "/{person_id}/film",
    response_model=list[MovieInfo],
    response_model_by_alias=True,
)
async def films(
    user: Annotated[dict, Depends(security_jwt)],
    person_id: UUID,
    limit_offset: Annotated[LimitOffset, Depends(LimitOffset)],
    person_service: PersonService = Depends(get_person_service),
) -> list[MovieInfo]:
    """Получить все фильмы по идентификатору персоны"""
    return await person_service.find_movies_by_person_uuid(person_uuid=person_id, limit_offset=limit_offset)


@router.get(
    path="",
    response_model=list[Person],
    response_model_by_alias=True,
)
async def persons(
    user: Annotated[dict, Depends(security_jwt)],
    limit_offset: Annotated[LimitOffset, Depends(LimitOffset)],
    sort: str = Query(
        default="id",
        regex=r"[+-]?(id)",
    ),
    person_service: PersonService = Depends(get_person_service),
) -> list[Person]:
    """Получить список всех персон"""
    return await person_service.find_persons(sort=sort, limit_offset=limit_offset)
