from datetime import datetime
from typing import Any

from pydantic import BaseModel


class BaseUGCModel(BaseModel):
    user_id: str
    movie_id: str


class BookmarkModel(BaseUGCModel):
    pass


class FilmRatingModel(BaseUGCModel):
    score: int


class ReviewRatingModel(BaseModel):
    review_id: str
    user_id: str
    score: int


class ReviewAvgRatingModel(BaseModel):
    review_id: str
    score: int
    quantity: int


class ReviewModel(BaseUGCModel):
    review_text: str
    score: int
    timestamp: datetime


class ViewModel(BaseUGCModel):
    chunk: int


class SavedDataModel(BaseModel):
    key: str
    value: dict[str, Any]

