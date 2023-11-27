import uuid
from functools import lru_cache

from fastapi import Depends

from db.user_repository import UserRepository, get_user_repository
from models.entities import User, UserHistory
from services.auth_service import RoleRepository, get_role_repository
from services.exceptions import BindEmptyRoles, BindUnknownRoles


class UserService:
    def __init__(self, user_repo: UserRepository, role_repo: RoleRepository) -> None:
        self._user_repo = user_repo
        self._role_repo = role_repo

    async def bind(self, user_id: uuid.UUID, role_ids: list[uuid.UUID]) -> User:
        user = await self._user_repo.get_user_by_id(user_id)
        roles = await self._role_repo.get_roles_by_ids(role_ids)

        if not roles:
            raise BindEmptyRoles("Bind empty roles")
        if len(roles) != len(role_ids):
            raise BindUnknownRoles(f"Bind unknown roles with ids={role_ids}")

        user.roles = roles
        user = await self._user_repo.update(user)

        return user

    async def history(self, user_id: uuid.UUID, limit: int, offset: int) -> UserHistory:
        user = await self._user_repo.get_user_by_id(user_id)

        return user.user_history[offset : offset + limit]

    async def all(self, limit: int, offset: int) -> [User]:
        users = await self._user_repo.list(limit=limit, offset=offset)

        return users


@lru_cache()
def get_user_service(
    user_repository: UserRepository = Depends(get_user_repository),
    role_repossitory: RoleRepository = Depends(get_role_repository),
) -> UserService:
    return UserService(user_repository, role_repossitory)
