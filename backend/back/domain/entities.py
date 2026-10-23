from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from typing import Any


@dataclass
class AuditRecord:
    thread_id: str
    role: str
    kind: str
    payload: dict[str, str] = field(default_factory=dict)
    at: str = ""


@dataclass
class RoleDef:
    name: str
    description: str
    system_prompt: str
    tools: Sequence[Any] = field(default_factory=list)
    model: str | None = None
    middleware: Sequence[Any] = field(default_factory=list)
    interrupt_on: dict[str, Any] | None = None
    skills: Sequence[str] = field(default_factory=list)
    response_format: Any | None = None
    builder: Callable[[], Any] | None = None


@dataclass
class McpServer:
    name: str
    description: str = ""
