from enum import Enum

import orjson
from fastapi import Query
from pydantic import UUID4, BaseModel, Field


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class Base(BaseModel):
    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class Role(str, Enum):
    ACTOR = "actor"
    DIRECTOR = "director"
    WRITER = "writer"


class PersonFilmsInfo(BaseModel):
    uuid: UUID4
    roles: list[Role]


class PersonInfo(Base):
    uuid: UUID4
    full_name: str
    films: list[PersonFilmsInfo]


class Person(Base):
    id: UUID4
    full_name: str = Field(..., alias="name")


class Actor(Person):
    pass


class Director(Person):
    pass


class Writer(Person):
    pass


class Genre(Base):
    uuid: UUID4 = Field(..., alias="id")
    name: str


class Movie(Base):
    uuid: UUID4 = Field(..., alias="id")
    title: str
    description: str | None
    imdb_rating: float
    genres: list[Genre]
    actors: list[Actor]
    writers: list[Writer]
    directors: list[Director]


class MovieInfo(Base):
    uuid: UUID4 = Field(..., alias="id")
    title: str
    imdb_rating: float


class LimitOffset(BaseModel):
    limit: int = Query(default=50, gt=0, alias="page_size", description="Количество элементов на странице")
    offset: int = Query(default=1, gt=0, alias="page_number", description="Номер страницы")


class SortField(BaseModel):
    operation: str
    field: str

    def __init__(self, sort_field_string, **data):
        map_ = {"-": "desc", "+": "asc"}
        if sort_field_string[0] in map_:
            super().__init__(operation=map_[sort_field_string[0]], field=sort_field_string[1:], **data)
        else:
            super().__init__(operation="asc", field=sort_field_string, **data)
