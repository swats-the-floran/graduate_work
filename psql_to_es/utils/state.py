from typing import Any

from utils.storage import BaseStorage


class State:
    def __init__(self, storage: BaseStorage):
        self.storage = storage

    def set_state(self, key: str, value: Any) -> None:
        self.storage.save_state(state={key: value})

    def get_state(self, key: str) -> Any:
        return self.storage.retrieve_state().get(key)
