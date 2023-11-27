import abc
import json
from typing import Any

from redis import Redis


class BaseStorage(abc.ABC):
    @abc.abstractmethod
    def save_state(self, state: dict) -> None:
        pass

    @abc.abstractmethod
    def retrieve_state(self) -> dict:
        pass


class JsonFileStorage(BaseStorage):
    def __init__(self, file_path: str | None):
        self.file_path = file_path

    def retrieve_state(self) -> dict:
        try:
            with open(self.file_path, "r") as json_file:
                data = json.load(json_file)
        except FileNotFoundError:
            data = {}
        return data

    def save_state(self, state: dict) -> None:
        with open(self.file_path, "w") as outfile:
            json.dump(state, outfile)


class RedisStorage(BaseStorage):
    def __init__(self, redis: Redis, volume: str) -> None:
        self._redis = redis
        self.volume = volume

    def save_state(self, state: dict[str, Any]) -> None:
        self._redis.hmset(self.volume, state)

    def retrieve_state(self) -> dict[str, Any]:
        return self._redis.hgetall(self.volume)
