import abc
from typing import Any

from . import index_settings as idx


class Index(abc.ABC):
    name: str
    redis_key: str
    settings: dict[str, Any] = idx.settings
    mappings: dict[str, Any]


class MovieIndex(Index):
    name = "movies"
    redis_key = "movies"
    mappings = idx.mappings_fw


class GenreIndex(Index):
    name = "genres"
    redis_key = "genres"
    mappings = idx.mappings_gn


class PersonIndex(Index):
    name = "persons"
    redis_key = "persons"
    mappings = idx.mappings_pr
