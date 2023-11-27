from http import HTTPStatus
from uuid import UUID

from async_fastapi_jwt_auth import AuthJWT
from fastapi import APIRouter, Depends, Query
from starlette.requests import Request
from starlette.responses import JSONResponse

from extensions.limiter import limiter
from schemas.response_schemas import FastAPIErrorResponse, FastAPIResponse, FastAPISuccessResponse
from db.exceptions import RoleAlreadyExists, RoleNotAuthenticated, RoleNotFound
from db.role_repository import RoleRepository, get_role_repository
from models.entities import Role, RoleName
from utils.jwt_checker import auth_required

router = APIRouter()


@router.post(
    path="/create/",
    responses={
        HTTPStatus.OK: {"model": FastAPISuccessResponse},
        HTTPStatus.CONFLICT: {"model": FastAPIErrorResponse},
    },
)
@auth_required([RoleName.ADMIN])
@limiter.limit('10/second')
async def create_role(
    request: Request,
    name: RoleName,
    role_repo: RoleRepository = Depends(get_role_repository),
    authorize: AuthJWT = Depends()
) -> FastAPIResponse:
    try:
        await role_repo.create(role=Role(name=name))
        return JSONResponse(status_code=HTTPStatus.OK, content={"result": "OK"})
    except (RoleAlreadyExists, RoleNotAuthenticated) as exc:
        return JSONResponse(status_code=HTTPStatus.CONFLICT, content={"detail": str(exc)})


@router.delete(
    path="/delete/{role_id}",
    responses={
        HTTPStatus.OK: {"model": FastAPISuccessResponse},
        HTTPStatus.NOT_FOUND: {"model": FastAPIErrorResponse},
    },
)
@auth_required([RoleName.ADMIN])
@limiter.limit('10/second')
async def delete_role(
    request: Request,
    role_id: UUID,
    role_repo: RoleRepository = Depends(get_role_repository),
    authorize: AuthJWT = Depends()
) -> FastAPIResponse:
    try:
        await role_repo.delete(id_=role_id)
        return JSONResponse(status_code=HTTPStatus.OK, content={"result": "OK"})
    except RoleNotFound as exc:
        return JSONResponse(status_code=HTTPStatus.NOT_FOUND, content={"detail": str(exc)})


@router.get(
    path="/list/",
    responses={
        HTTPStatus.OK: {"model": FastAPISuccessResponse},
        HTTPStatus.NOT_FOUND: {"model": FastAPIErrorResponse},
    },
)
@auth_required([RoleName.ADMIN])
@limiter.limit('10/second')
async def roles(
    request: Request,
    page_size: int = Query(default=50, gt=0),
    page_number: int = Query(default=1, gt=0),
    role_repo: RoleRepository = Depends(get_role_repository),
    authorize: AuthJWT = Depends(),
) -> FastAPIResponse:
    offset = (page_number - 1) * page_size
    try:
        all_roles = await role_repo.list(limit=page_size, offset=offset)
        return JSONResponse(status_code=HTTPStatus.OK, content={"result": [role.as_dict() for role in all_roles]})
    except RoleNotFound as exc:
        return JSONResponse(status_code=HTTPStatus.NOT_FOUND, content={"detail": str(exc)})


@router.get(
    path="/",
    responses={
        HTTPStatus.OK: {"model": FastAPISuccessResponse},
        HTTPStatus.NOT_FOUND: {"model": FastAPIErrorResponse},
        HTTPStatus.BAD_REQUEST: {"model": FastAPIErrorResponse},
    },
)
@auth_required([RoleName.ADMIN])
@limiter.limit('10/second')
async def get_role(
    request: Request,
    name: RoleName | None = None,
    role_id: UUID | None = None,
    role_repo: RoleRepository = Depends(get_role_repository),
    authorize: AuthJWT = Depends(),
) -> FastAPIResponse:
    if not name and not role_id:
        return JSONResponse(
            status_code=HTTPStatus.BAD_REQUEST, content={"error": "at least one parameter should be provide"}
        )
    else:
        try:
            if name:
                role = await role_repo.get_role_by_name(name=name)
            elif role_id:
                role = await role_repo.get_role_by_id(id_=role_id)
            return JSONResponse(status_code=HTTPStatus.OK, content={"result": role.as_dict()})
        except RoleNotFound as exc:
            return JSONResponse(status_code=HTTPStatus.NOT_FOUND, content={"detail": str(exc)})
