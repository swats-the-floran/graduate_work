import uuid
from functools import lru_cache
from typing import List

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from db.exceptions import RoleAlreadyExists, RoleNotFound
from db.postgres import get_async_session
from models.entities import Role, RoleName


class RoleRepository:
    def __init__(self, async_session: AsyncSession) -> None:
        self._async_session = async_session

    async def create(self, role: Role) -> Role:
        self._async_session.add(role)
        try:
            await self._async_session.commit()
        except IntegrityError:
            raise RoleAlreadyExists("Role with name={0} already exists".format(role.name.value))

        await self._async_session.refresh(role)
        return role

    async def delete(self, id_: uuid.UUID) -> None:
        try:
            role = (await self._async_session.execute(select(Role).where(Role.id == id_))).first()[0]
        except:
            raise RoleNotFound("Role with id={0} not found".format(str(id_)))
        await self._async_session.delete(role)
        await self._async_session.commit()

    async def list(self, limit: int, offset: int) -> list[Role]:
        query = select(Role).limit(limit).offset(offset)
        result = await self._async_session.execute(query)
        return list(result.scalars().all())

    async def get_role_by_name(self, name: RoleName) -> Role:
        query = select(Role).where(Role.name == name)
        result = await self._async_session.execute(query)
        if role := result.scalar():
            return role
        raise RoleNotFound("Role with name={0} not found".format(str(name)))

    async def get_role_by_id(self, id_: uuid.UUID) -> Role:
        query = select(Role).where(Role.id == id_)
        result = await self._async_session.execute(query)
        if role := result.scalar():
            return role
        raise RoleNotFound("Role with id={0} not found".format(str(id_)))

    async def get_roles_by_ids(self, role_ids: List[uuid.UUID]) -> List[Role]:
        query = select(Role).filter(Role.id.in_(role_ids))
        result = await self._async_session.execute(query)
        return list(result.scalars().all())


@lru_cache()
def get_role_repository(session: AsyncSession = Depends(get_async_session)) -> RoleRepository:
    return RoleRepository(session)
