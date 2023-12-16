import logging
from functools import lru_cache
from fastapi import Depends

from motor.motor_asyncio import AsyncIOMotorClient

from db.mongo_helper import MongoMixin, get_mongo_client
from models.models import FilmAvgRatingModel

logger = logging.getLogger(__name__)


class FilmRatingsService(MongoMixin):

    async def get_list(self, subquery: list[str]) -> list[FilmAvgRatingModel]:
        query = [
          {
            "$match": {
              "movie_id": {
                "$in": subquery
              },
              "score": {
                "$exists": True
              }
            }
          },
          {
            "$group": {
              "_id": "$movie_id",
              "movie_id": {
                "$first": "$movie_id"
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

        return [FilmAvgRatingModel(**doc) async for doc in self.collection.aggregate(query)]


@lru_cache
def get_service(
    client: AsyncIOMotorClient = Depends(get_mongo_client),
    db_name: str = 'movies',
    table_name: str = 'film_ratings',
) -> FilmRatingsService:
    return FilmRatingsService(client, db_name, table_name)
