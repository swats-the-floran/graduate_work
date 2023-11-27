from datetime import datetime
from typing import Any

from pydantic import BaseModel


class BaseUGCModel(BaseModel):
    user_id: int
    movie_id: int


class BookmarkModel(BaseUGCModel):
    pass


class FilmRatingModel(BaseUGCModel):
    score: int


class ReviewRatingModel(BaseUGCModel):
    author_id: int
    score: int


class ReviewModel(BaseUGCModel):
    review_text: str
    score: int
    timestamp: datetime


class ViewModel(BaseUGCModel):
    chunk: int


class SavedDataModel(BaseModel):
    key: str
    value: dict[str, Any]

