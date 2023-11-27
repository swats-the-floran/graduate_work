from abc import ABC, abstractmethod

from models.models import BaseUGCModel, SavedDataModel


class DBInterface(ABC):
    """DB client should save data, find it and delete."""

    @abstractmethod
    async def create(self, *args, **kwargs) -> SavedDataModel:
        pass

    @abstractmethod
    async def get_one(self, *args, **kwargs) -> BaseUGCModel:
        pass

    @abstractmethod
    async def get_list(self, *args, **kwargs) -> list[BaseUGCModel]:
        pass

    @abstractmethod
    async def delete(self, *args, **kwargs) -> None:
        pass

