from functools import wraps
from http import HTTPStatus

from async_fastapi_jwt_auth import AuthJWT
from fastapi import HTTPException

from models.entities import RoleName


def auth_required(access_roles: list[RoleName]):
    def api_route(router):
        @wraps(router)
        async def check_autorization(authorize: AuthJWT, *args, **kwargs):
            await authorize.jwt_required()
            roles = (await authorize.get_raw_jwt())["roles"]
            access = [role.value for role in access_roles]
            if RoleName.ADMIN in roles:
                return await router(*args, **kwargs)
            if not (set(access) & set(roles)):
                raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="Forbidden")
            if kwargs.get("user_id") and str(kwargs["user_id"]) != (await authorize.get_jwt_subject()):
                raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="Forbidden")
            return await router(*args, **kwargs)

        return check_autorization

    return api_route
