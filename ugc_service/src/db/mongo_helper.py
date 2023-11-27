from abc import abstractmethod
from http import HTTPStatus
from typing import Optional
from fastapi import HTTPException

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import DuplicateKeyError

from db.database import DBInterface
from models.models import BaseUGCModel, SavedDataModel

client: Optional[AsyncIOMotorClient] = None


async def get_mongo_client() -> Optional[AsyncIOMotorClient]:
    return client


class MongoMixin(DBInterface):

    def __init__(self, client: AsyncIOMotorClient, db_name: str, table_name: str) -> None:
        self.client = client
        self.db = client[db_name]
        self.collection = self.db.get_collection(table_name)

    async def create(self, query: dict) -> SavedDataModel:
        try:
            record = await self.collection.insert_one(query)
        except DuplicateKeyError:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='This record already exists.'
            )

        return SavedDataModel(key=str(record.inserted_id), value=query)


    async def get_one(self, *args, **kwargs) -> BaseUGCModel:
        pass

    async def get_list(self, *args, **kwargs) -> list[BaseUGCModel]:
        pass

    async def delete(self, query: dict) -> None:
        obj = await self.collection.find_one_and_delete(query, projection={"_id": False})

        if not obj:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Not found.')
