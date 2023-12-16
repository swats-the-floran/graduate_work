import aiohttp
import concurrent.futures
import secrets
import uuid
from async_fastapi_jwt_auth import AuthJWT
from datetime import datetime
from fastapi import Depends
from functools import lru_cache
from functools import partial
from redis.asyncio import Redis
import asyncio
from typing import Any
from werkzeug.security import check_password_hash, generate_password_hash

from core.jwt_config import setting_jwt
from core.tasks import register_new_profile
from db.exceptions import UserNotFound, SocialAccountNotFound
from db.postgres import get_async_session
from db.redis import get_redis
from db.role_repository import RoleRepository
from db.social_repository import SocialRepository
from db.user_repository import UserRepository, get_user_repository
from models.entities import Role, RoleName, User, UserHistory, SocialAccount


class FakeEmailClient:
    def __init__(self) -> None:
        self.send_count = 0

    def send(self, *args, **kwargs):
        self.send_count += 1


class PasswordNotEqual(Exception):
    pass


class AuthService:
    def __init__(
        self,
        user_repo: UserRepository,
        social_repo: SocialRepository,
        role_repository: RoleRepository,
        email_client: FakeEmailClient,
        redis: Redis,
    ) -> None:
        self._user_repo = user_repo
        self._social_repo = social_repo
        self._role_repository = role_repository
        self._email_client = email_client
        self._redis = redis

    async def sign_up(self, email: str, password: str, first_name: str, second_name: str) -> User:
        registered_role = await self._role_repository.get_role_by_name(RoleName.REGISTERED)
        user = await self._user_repo.create(
            user=User(
                email=email,
                password=generate_password_hash(password),
                roles=[registered_role],
                first_name=first_name,
                second_name=second_name,
            ),
        )
        profile_json = {
            "password": password,
            "email": email
        }

        call = partial(register_new_profile.apply_async, (profile_json,))
        loop = asyncio.get_running_loop()
        with concurrent.futures.ThreadPoolExecutor() as pool:
            await loop.run_in_executor(pool, call)

        self._email_client.send(email=user.email)
        return user

    async def sign_in(self, email: str, password: str, auth_data: dict[str, Any]) -> User:
        user = await self._user_repo.get_user_by_email(email=email)
        if not check_password_hash(user.password, password):
            raise PasswordNotEqual("Passwords not equal")

        user.user_history.append(UserHistory(last_login_datetime=datetime.now(), device=auth_data["device"]))
        user = await self._user_repo.update(user)

        return user

    async def auth_by_social(self, auth_profile: dict[str, Any], auth_data: dict[str, Any]):
        email = auth_profile.get('email', '')
        try:
            user = await self._user_repo.get_user_by_email(email=email)
            user.user_history.append(
                UserHistory(last_login_datetime=datetime.now(),
                            device=auth_data["device"]))
            await self._user_repo.update(user)
        except UserNotFound:
            user = await self.sign_up(email=email, password=secrets.token_urlsafe(8), first_name='', second_name='')

        try:
            social_account = await self._social_repo.get_social_repo_by_user_id(
                user.id)
            await self._social_repo.update(social_account)
        except SocialAccountNotFound:
            await self._social_repo.create(
                SocialAccount(
                    user_id=user.id,
                    social_id=auth_profile['social_id'],
                    social_name=auth_profile['social_name']
                )
            )

        return user

    async def change_password(self, user_id: uuid.UUID, old_password: str, new_password: str) -> User:
        user = await self._user_repo.get_user_by_id(id_=user_id)
        if not check_password_hash(user.password, old_password):
            raise PasswordNotEqual("Old password not equal")

        user.password = generate_password_hash(new_password)
        user = await self._user_repo.update(user)

        self._email_client.send(user.email)

        return user

    async def create_both_tokens(self, authorize: AuthJWT, user_id: str) -> (str, str):
        user = await self._user_repo.get_user_by_id(uuid.UUID(user_id))
        roles = [role.name.value for role in user.roles]
        access_token = await authorize.create_access_token(subject=user_id, user_claims=dict(roles=roles, email=user.email))
        access_jti = await authorize.get_jti(access_token)

        refresh_token = await authorize.create_refresh_token(
            subject=user_id, user_claims={"access_jti": access_jti, "roles": roles}
        )

        return access_token, refresh_token

    async def revoke_both_tokens(self, authorize: AuthJWT) -> None:
        refresh_jti = (await authorize.get_raw_jwt())["jti"]
        access_jti = (await authorize.get_raw_jwt())["access_jti"]
        await self._redis.setex(access_jti, setting_jwt.access_expires, "true")
        await self._redis.setex(refresh_jti, setting_jwt.refresh_expires, "true")

    async def is_registered(self, user_id: str) -> User:
        user = await self._user_repo.get_user_by_id(uuid.UUID(user_id))
        return user


@lru_cache()
def get_role_repository(session=Depends(get_async_session)) -> RoleRepository:
    return RoleRepository(session)


@lru_cache()
def get_social_repository(session=Depends(get_async_session)) -> SocialRepository:
    return SocialRepository(session)


@lru_cache()
def get_auth_service(
        user_repository: UserRepository = Depends(get_user_repository),
        role_repossitory: RoleRepository = Depends(get_role_repository),
        social_repository: SocialRepository = Depends(get_social_repository),
        redis: Redis = Depends(get_redis),
) -> AuthService:
    return AuthService(user_repository, social_repository, role_repossitory, FakeEmailClient(), redis)
