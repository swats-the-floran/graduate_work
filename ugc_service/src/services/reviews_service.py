import logging
from datetime import datetime
from functools import lru_cache
from fastapi import Depends

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ReturnDocument

from db.mongo_helper import MongoMixin, get_mongo_client
from models.models import ReviewModel, SavedDataModel

logger = logging.getLogger(__name__)


class ReviewsService(MongoMixin):

    async def get_list(self, query: dict) -> list[ReviewModel]:
        return [ReviewModel(**doc) async for doc in self.collection.find(query)]

    async def update(self, document: dict) -> SavedDataModel:
        query = {"user_id": document['user_id'], "movie_id": document['movie_id']}
        query['timestamp'] = datetime.now()

        record = await self.collection.find_one_and_replace(
            query,
            document,
            projection={"_id": False},
            return_document=ReturnDocument.AFTER,
            upsert=True,
        )

        return SavedDataModel(key=str(record.id), value=query)


@lru_cache
def get_service(
    client: AsyncIOMotorClient = Depends(get_mongo_client),
    db_name: str = 'movies',
    table_name: str = 'reviews',
) -> ReviewsService:
    return ReviewsService(client, db_name, table_name)
