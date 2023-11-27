import logging
from functools import lru_cache
from fastapi import Depends

from motor.motor_asyncio import AsyncIOMotorClient

from db.mongo_helper import MongoMixin, get_mongo_client
from models.models import ReviewRatingModel

logger = logging.getLogger(__name__)


class ReviewRatingsService(MongoMixin):

    async def get_list(self, query: dict) -> list[ReviewRatingModel]:
        return [ReviewRatingModel(**doc) async for doc in self.collection.find(query)]


@lru_cache
def get_service(
    client: AsyncIOMotorClient = Depends(get_mongo_client),
    db_name: str = 'movies',
    table_name: str = 'review_ratings',
) -> ReviewRatingsService:
    return ReviewRatingsService(client, db_name, table_name)
