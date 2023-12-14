import logging
from functools import lru_cache
from fastapi import Depends

from motor.motor_asyncio import AsyncIOMotorClient

from db.mongo_helper import MongoMixin, get_mongo_client
from models.models import ReviewAvgRatingModel

logger = logging.getLogger(__name__)


class ReviewRatingsService(MongoMixin):

    async def get_list(self, subquery: list[str]) -> list[ReviewAvgRatingModel]:
        query = [
          {
            "$match": {
              "review_id": {
                "$in": subquery
              },
              "score": {
                "$exists": True
              }
            }
          },
          {
            "$group": {
              "_id": "$review_id",
              "review_id": {
                "$first": "$review_id"
              },
              "score": {
                "$avg": "$score"
              },
              "quantity": {
                "$sum": 1
              }
            }
          }
        ]

        return [ReviewAvgRatingModel(**doc) async for doc in self.collection.aggregate(query)]


@lru_cache
def get_service(
    client: AsyncIOMotorClient = Depends(get_mongo_client),
    db_name: str = 'movies',
    table_name: str = 'review_ratings',
) -> ReviewRatingsService:
    return ReviewRatingsService(client, db_name, table_name)
