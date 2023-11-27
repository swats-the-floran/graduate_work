import uuid
from functools import lru_cache

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from db.exceptions import UserAlreadyExists, UserNotFound
from db.postgres import get_async_session
from models.entities import User


class UserRepository:
    def __init__(self, async_session: AsyncSession) -> None:
        self._async_session = async_session

    async def create(self, user: User) -> User:
        self._async_session.add(user)
        try:
            await self._async_session.commit()
        except IntegrityError:
            raise UserAlreadyExists(f"User with email={user.email} already exists")

        await self._async_session.refresh(user)
        return user

    async def update(self, user: User) -> User:
        self._async_session.add(user)
        await self._async_session.commit()
        await self._async_session.refresh(user)
        return user

    async def list(self, limit: int, offset: int) -> list[User]:
        query = select(User).limit(limit).offset(offset)
        result = await self._async_session.execute(query)
        return result.scalars().all()

    async def get_user_by_email(self, email: str) -> User:
        query = select(User).where(User.email == email)
        result = await self._async_session.execute(query)
        if user := result.scalar():
            return user
        raise UserNotFound(f"User with email={email} not found")

    async def get_user_by_id(self, id_: uuid.UUID) -> User:
        query = select(User).where(User.id == id_)
        result = await self._async_session.execute(query)
        if user := result.scalar():
            return user
        raise UserNotFound(f"User with id={id_} not found")


@lru_cache()
def get_user_repository(session: AsyncSession = Depends(get_async_session)) -> UserRepository:
    return UserRepository(session)
