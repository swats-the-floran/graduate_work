from enum import Enum


class FilmworkTypeEnum(str, Enum):
    MOVIE = "movie"
    TV_SHOW = "tv_show"


class PersonRoleEnum(str, Enum):
    ACTOR = "actor"
    WRITER = "writer"
    DIRECTOR = "director"
