from http import HTTPStatus
from uuid import UUID

from async_fastapi_jwt_auth import AuthJWT
from fastapi import APIRouter, Depends, Header, Query
from fastapi.responses import JSONResponse
from pydantic import EmailStr
from fastapi import Request

from schemas.response_schemas import FastAPIErrorResponse, FastAPIResponse, FastAPISuccessResponse
from db.exceptions import UserAlreadyExists, UserNotFound
from models.entities import RoleName
from services.auth_service import AuthService, PasswordNotEqual, get_auth_service
from utils.jwt_checker import auth_required

from extensions.limiter import limiter

router = APIRouter()

# https://stackoverflow.com/questions/2990654/how-to-test-a-regex-password-in-python
PASSWORD_REGEX = r"[A-Za-z0-9@#$%^&+=]{8,}"

# Регулярные выражения с positive lookahead (?=) больше не поддерживаются
# PASSWORD_REGEX = r"^(?=.*[0-9].*)(?=.*[a-z].*)(?=.*[A-Z].*)[0-9a-zA-Z]{8,}$"
# 1. (?=.*[0-9]) - строка содержит хотя бы одно число;
# 2. (?=.*[a-z]) - строка содержит хотя бы одну латинскую букву в нижнем регистре;
# 3. (?=.*[A-Z]) - строка содержит хотя бы одну латинскую букву в верхнем регистре;
# 4. 0-9a-zA-Z]{8,} - строка состоит не менее, чем из 8 вышеупомянутых символов.


@router.post(
    path="/sign_up/",
    responses={
        HTTPStatus.OK: {"model": FastAPISuccessResponse},
        HTTPStatus.CONFLICT: {"model": FastAPIErrorResponse},
    },
)
@limiter.limit('10/second')
async def sign_up(
        request: Request,
        email: EmailStr,
        password: str = Query(regex=PASSWORD_REGEX),
        auth_service: AuthService = Depends(get_auth_service),
        first_name: str = "",
        second_name: str = "",
) -> FastAPIResponse:
    """Зарегистрировать пользователя

    Args:
        request: объект запроса, нужен для работы лимитера запросов
        email: электронная почта пользователя
        password: пароль пользователя
        first_name: имя пользователя
        second_name: фамилия пользователя.
    """
    try:
        await auth_service.sign_up(email=email, password=password, first_name=first_name, second_name=second_name)
        return JSONResponse(status_code=HTTPStatus.OK, content={"result": "OK"})
    except UserAlreadyExists as exc:
        return JSONResponse(status_code=HTTPStatus.CONFLICT, content={"detail": str(exc)})


@router.post(
    path="/sign_in/",
    responses={
        HTTPStatus.OK: {"model": FastAPISuccessResponse},
        HTTPStatus.CONFLICT: {"model": FastAPIErrorResponse},
        HTTPStatus.NOT_FOUND: {"model": FastAPIErrorResponse},
    },
)
@limiter.limit('10/second')
async def sign_in(
    request: Request,
    email: EmailStr,
    password: str = Query(min_length=8),
    auth_service: AuthService = Depends(get_auth_service),
    user_agent: str = Header(None, include_in_schema=False),
    authorize: AuthJWT = Depends(),
) -> FastAPIResponse:
    """Авторизовать пользователя

    Args:
        request: объект запроса, нужен для работы лимитера запросов
        email: электронная почта пользователя
        password: пароль пользователя.
    """
    try:
        user = await auth_service.sign_in(email=email, password=password, auth_data={"device": user_agent})
        access_token, refresh_token = await auth_service.create_both_tokens(authorize, str(user.id))

        return JSONResponse(
            status_code=HTTPStatus.OK, content={"user": user.as_dict(), "access_token": access_token, "refresh_token": refresh_token}
        )
    except PasswordNotEqual as exc:
        return JSONResponse(status_code=HTTPStatus.FORBIDDEN, content={"detail": str(exc)})
    except UserNotFound as exc:
        return JSONResponse(status_code=HTTPStatus.NOT_FOUND, content={"detail": str(exc)})


@router.post(
    path="/change_password/",
    responses={
        HTTPStatus.OK: {"model": FastAPISuccessResponse},
        HTTPStatus.CONFLICT: {"model": FastAPIErrorResponse},
        HTTPStatus.NOT_FOUND: {"model": FastAPIErrorResponse},
    },
)
@auth_required([RoleName.ADMIN, RoleName.REGISTERED])
@limiter.limit('10/second')
async def change_password(
    request: Request,
    user_id: UUID,
    old: str = Query(min_length=8),
    new: str = Query(regex=PASSWORD_REGEX),
    auth_service: AuthService = Depends(get_auth_service),
    authorize: AuthJWT = Depends(),
) -> FastAPIResponse:
    """Сменить пароль пользователя

    Args:
        authorize: объект запроса, нужен для работы лимитера запросов
        email: электронная почта пользователя
        old: страый пароль пользователя
        new: новый пароль пользователя
    """
    try:
        await auth_service.change_password(user_id=user_id, old_password=old, new_password=new)
        return JSONResponse(status_code=HTTPStatus.OK, content={"result": "OK"})
    except PasswordNotEqual as exc:
        return JSONResponse(status_code=HTTPStatus.FORBIDDEN, content={"detail": str(exc)})
    except UserNotFound as exc:
        return JSONResponse(status_code=HTTPStatus.NOT_FOUND, content={"detail": str(exc)})


@router.post("/refresh/")
async def refresh(
    request: Request,
    authorize: AuthJWT = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
) -> JSONResponse:
    await authorize.jwt_refresh_token_required()
    current_user_id = await authorize.get_jwt_subject()
    await auth_service.revoke_both_tokens(authorize)
    new_access_token, refresh_token = await auth_service.create_both_tokens(authorize, current_user_id)

    return JSONResponse(status_code=HTTPStatus.OK, content={"access_token": new_access_token})


@router.delete("/logout/")
@limiter.limit('10/second')
async def logout(
        request: Request,
        authorize: AuthJWT = Depends(),
        auth_service: AuthService = Depends(get_auth_service)
) -> JSONResponse:
    await authorize.jwt_refresh_token_required()
    await auth_service.revoke_both_tokens(authorize)

    return JSONResponse(status_code=HTTPStatus.OK, content={"result": "OK"})


@router.get(
    path="/me/",
    responses={
        HTTPStatus.OK: {"model": FastAPISuccessResponse},
        HTTPStatus.BAD_REQUEST: {"model": FastAPIErrorResponse},
    },
)
async def check_me(
    authorize: AuthJWT = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
) -> JSONResponse:
    """Узнать зарегистрирован ли пользователь"""
    await authorize.jwt_required()
    current_user_id = await authorize.get_jwt_subject()
    try:
        await auth_service.is_registered(user_id=current_user_id)
        return JSONResponse(status_code=HTTPStatus.OK, content={"result": "OK"})
    except UserNotFound as exc:
        return JSONResponse(status_code=HTTPStatus.NOT_FOUND, content={"detail": str(exc)})
