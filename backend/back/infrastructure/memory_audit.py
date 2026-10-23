from __future__ import annotations

from datetime import UTC, datetime

from ..application.interfaces import AuditWriter
from ..domain.entities import AuditRecord


class InMemoryAuditWriter(AuditWriter):
    def __init__(self) -> None:
        self._log: list[AuditRecord] = []

    def write(
        self,
        thread_id: str,
        role: str,
        kind: str,
        payload: dict[str, str] | None = None,
    ) -> AuditRecord:
        record = AuditRecord(
            thread_id=thread_id,
            role=role,
            kind=kind,
            payload=dict(payload or {}),
            at=datetime.now(UTC).isoformat(),
        )
        self._log.append(record)
        return record

    def list_records(self) -> list[AuditRecord]:
        return list(self._log)

    def clear(self) -> None:
        self._log.clear()
