from typing import Protocol

from ..domain.entities import AuditRecord
from .dto import ChatOutput


class AuditWriter(Protocol):
    def write(
        self,
        thread_id: str,
        role: str,
        kind: str,
        payload: dict[str, str] | None = None,
    ) -> AuditRecord: ...
    def list_records(self) -> list[AuditRecord]: ...
    def clear(self) -> None: ...


class IdempotencyStore(Protocol):
    def get(self, key: str) -> ChatOutput | None: ...
    def put(self, key: str, value: ChatOutput) -> None: ...
    def clear(self) -> None: ...


class ConversationRunner(Protocol):
    def run(self, message: str, thread_id: str) -> str: ...


class RoleRunner(Protocol):
    def __call__(self, role: str, query: str) -> str: ...
