from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass
class AuditRecord:
    thread_id: str
    role: str
    kind: str
    payload: dict[str, str] = field(default_factory=dict)
    at: str = ""


_log: list[AuditRecord] = []


def write_audit(
    thread_id: str, role: str, kind: str, payload: dict[str, str] | None = None
) -> AuditRecord:
    record = AuditRecord(
        thread_id=thread_id,
        role=role,
        kind=kind,
        payload=dict(payload or {}),
        at=datetime.now(UTC).isoformat(),
    )
    _log.append(record)
    return record


def list_audits() -> list[AuditRecord]:
    return list(_log)


def clear_audits() -> None:
    _log.clear()
