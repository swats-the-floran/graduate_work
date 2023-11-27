class BaseDBException(Exception):
    pass


class SaveDBException(BaseDBException):
    """Ошибка сохранения в базу данных"""


class SelectDBException(BaseDBException):
    """Ошибка получения данных из базы данных"""
