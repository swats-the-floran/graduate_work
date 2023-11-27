from pydantic import Field
from pydantic_settings import BaseSettings


class BaseConfig(BaseSettings):
    MONGODB_HOST: str = Field(env="MONGODB_HOST", default="localhost:27019")

    DB_NAME: str = Field(env="DB_NAME", default="movies")
    BOOKMARKS_TABLE_NAME: str = Field(env="BOOKMARKS_TABLE_NAME", default="bookmarks")
    FILM_RATINGS_TABLE_NAME: str = Field(env="FILM_RATINGS_TABLE_NAME", default="film_ratings")
    REVIEW_RATINGS_TABLE_NAME: str = Field(env="REVIEW_RATINGS_TABLE_NAME", default="review_ratings")
    REVIEWS_TABLE_NAME: str = Field(env="REVIEWS_TABLE_NAME", default="reviews")
    VIEWS_TABLE_NAME: str = Field(env="VIEWS_TABLE_NAME", default="views")

# settings: BaseConfig = BaseConfig()

