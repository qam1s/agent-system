from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from typing import Any, TypedDict


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


@dataclass
class Source:
    id: str
    title: str
    text: str


class Hit(TypedDict):
    id: str
    title: str
    text: str
    score: int


class Route(TypedDict):
    role: str
    confidence: float


class GateVerdict(TypedDict):
    passed: bool
    issues: list[str]
