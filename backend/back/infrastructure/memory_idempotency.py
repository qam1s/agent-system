from ..application.dto import ChatOutput
from ..application.interfaces import IdempotencyStore


class InMemoryIdempotencyStore(IdempotencyStore):
    def __init__(self) -> None:
        self._store: dict[str, ChatOutput] = {}

    def get(self, key: str) -> ChatOutput | None:
        return self._store.get(key)

    def put(self, key: str, value: ChatOutput) -> None:
        self._store[key] = value

    def clear(self) -> None:
        self._store.clear()
