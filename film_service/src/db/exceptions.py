class BaseRepositoryException(Exception):
    def __init__(self, detail: str) -> None:
        self.detail = detail


class MovieNotFoundException(BaseRepositoryException):
    """Фильм не найден в ES"""


class GenreNotFoundException(BaseRepositoryException):
    """Жанр не найден в ES"""


class PersonNotFoundException(BaseRepositoryException):
    """Персона не найдена в ES"""
