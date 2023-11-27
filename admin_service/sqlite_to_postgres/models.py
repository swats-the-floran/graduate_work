from __future__ import annotations

import abc
import datetime
import uuid
from dataclasses import dataclass, fields
from decimal import Decimal
from typing import Any

from enums import FilmworkTypeEnum, PersonRoleEnum
from helpers import make_date, make_datetime


class BaseModel(abc.ABC):
    @classmethod
    def get_field_names_for_query_sqlite(cls) -> str:
        query = ",".join((field.name for field in fields(cls)))
        return query.replace("created", "created_at as created").replace("modified", "updated_at as modified")

    @classmethod
    @abc.abstractmethod
    def from_dict(cls, query_row: dict[str, Any]) -> BaseModel:
        pass

    @property
    @abc.abstractmethod
    def values(self) -> str:
        pass

    @staticmethod
    @abc.abstractmethod
    def keys_to_psql() -> str:
        pass

    class Config:
        table_name = None


@dataclass
class FilmworkModel(BaseModel):
    id: uuid.uuid4
    title: str
    description: str
    creation_date: datetime.date | None
    rating: Decimal
    type: FilmworkTypeEnum
    created: datetime.datetime
    modified: datetime.datetime

    @property
    def values(self) -> str:
        return (
            self.id,
            self.title,
            self.description,
            self.creation_date,
            self.rating,
            self.type,
            self.created,
            self.modified,
        )

    @staticmethod
    def keys_to_psql() -> str:
        return "id, title, description, creation_date, rating, type, created, modified"

    @classmethod
    def from_dict(cls, query_row: dict[str, Any]) -> FilmworkModel:
        return cls(
            id=query_row["id"],
            title=query_row["title"],
            description=query_row["description"],
            creation_date=make_date(query_row["creation_date"]),
            rating=cls._get_rating(query_row["rating"]),
            type=FilmworkTypeEnum(query_row["type"]),
            created=make_datetime(query_row["created"]),
            modified=make_datetime(query_row["modified"]),
        )

    @classmethod
    def _get_rating(cls, rating: str | None) -> Decimal:
        if rating is not None:
            return Decimal(rating).quantize(Decimal("1.00"))
        return Decimal("0.00")

    class Config:
        table_name = "film_work"


@dataclass
class PersonModel(BaseModel):
    id: uuid.uuid4
    full_name: str
    created: datetime.datetime
    modified: datetime.datetime

    @property
    def values(self) -> str:
        return (
            self.id,
            self.full_name,
            self.created,
            self.modified,
        )

    @staticmethod
    def keys_to_psql() -> str:
        return "id, full_name, created, modified"

    @classmethod
    def from_dict(cls, query_row: dict[str, Any]) -> PersonModel:
        return cls(
            id=query_row["id"],
            full_name=query_row["full_name"],
            created=make_datetime(query_row["created"]),
            modified=make_datetime(query_row["modified"]),
        )

    class Config:
        table_name = "person"


@dataclass
class GenreModel(BaseModel):
    id: uuid.uuid4
    name: str
    description: str
    created: datetime.datetime
    modified: datetime.datetime

    @property
    def values(self) -> str:
        return (
            self.id,
            self.name,
            self.description,
            self.created,
            self.modified,
        )

    @staticmethod
    def keys_to_psql() -> str:
        return "id, name, description, created, modified"

    @classmethod
    def from_dict(cls, query_row: dict[str, Any]) -> GenreModel:
        return cls(
            id=query_row["id"],
            name=query_row["name"],
            description=query_row["description"],
            created=make_datetime(query_row["created"]),
            modified=make_datetime(query_row["modified"]),
        )

    class Config:
        table_name = "genre"


@dataclass
class GenreFilmworkModel(BaseModel):
    id: uuid.uuid4
    film_work_id: uuid.uuid4
    genre_id: uuid.uuid4
    created: datetime.datetime

    @property
    def values(self) -> str:
        return (
            self.id,
            self.film_work_id,
            self.genre_id,
            self.created,
        )

    @staticmethod
    def keys_to_psql() -> str:
        return "id, film_work_id, genre_id, created"

    @classmethod
    def from_dict(cls, query_row: dict[str, Any]) -> GenreModel:
        return cls(
            id=query_row["id"],
            film_work_id=query_row["film_work_id"],
            genre_id=query_row["genre_id"],
            created=make_datetime(query_row["created"]),
        )

    class Config:
        table_name = "genre_film_work"


@dataclass
class PersonFilmworkModel(BaseModel):
    id: uuid.uuid4
    film_work_id: uuid.uuid4
    person_id: uuid.uuid4
    role: PersonRoleEnum
    created: datetime.datetime

    @property
    def values(self) -> str:
        return (
            self.id,
            self.film_work_id,
            self.person_id,
            self.role,
            self.created,
        )

    @staticmethod
    def keys_to_psql() -> str:
        return "id, film_work_id, person_id, role, created"

    @classmethod
    def from_dict(cls, query_row: dict[str, Any]) -> GenreModel:
        return cls(
            id=query_row["id"],
            film_work_id=query_row["film_work_id"],
            person_id=query_row["person_id"],
            role=PersonRoleEnum(query_row["role"]),
            created=make_datetime(query_row["created"]),
        )

    class Config:
        table_name = "person_film_work"
