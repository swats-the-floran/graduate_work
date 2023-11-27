from abc import ABC, abstractmethod


class BrokerInterface(ABC):
    """Broker should get messages from api and save them."""

    @abstractmethod
    def set_data(self, key: str, data: str, *args, **kwargs) -> None:
        pass
