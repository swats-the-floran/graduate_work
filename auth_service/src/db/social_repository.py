import uuid
from functools import lru_cache

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from db.exceptions import SocialAccountAlreadyExists, SocialAccountNotFound
from db.postgres import get_async_session
from models.entities import SocialAccount


class SocialRepository:
    def __init__(self, async_session: AsyncSession) -> None:
        self._async_session = async_session

    async def create(self, social_account: SocialAccount) -> SocialAccount:
        self._async_session.add(social_account)
        try:
            await self._async_session.commit()
        except IntegrityError:
            raise SocialAccountAlreadyExists(f"Social account with social_id={social_account.social_id} already exists")

        await self._async_session.refresh(social_account)
        return social_account

    async def update(self, social_account: SocialAccount) -> SocialAccount:
        self._async_session.add(social_account)
        await self._async_session.commit()
        await self._async_session.refresh(social_account)
        return social_account

    async def get_social_repo_by_user_id(self, id_: uuid.UUID) -> SocialAccount:
        query = select(SocialAccount).where(SocialAccount.user_id == id_)
        result = await self._async_session.execute(query)
        if social_account := result.scalar():
            return social_account
        raise SocialAccountNotFound(f"User with id={id_} not found")

@lru_cache()
def get_social_repository(session: AsyncSession = Depends(get_async_session)) -> SocialRepository:
    return SocialRepository(session)
