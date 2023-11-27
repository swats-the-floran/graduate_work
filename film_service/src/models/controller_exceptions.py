from pydantic import BaseModel


class MovieNotFound(BaseModel):
    """Ошибка вызываемая в контроллере"""

    detail: str


class GenreNotFound(BaseModel):
    """Ошибка вызываемая в контроллере"""

    detail: str


class PersonNotFound(BaseModel):
    """Ошибка вызываемая в контроллере"""

    detail: str
