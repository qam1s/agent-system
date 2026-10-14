from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from typing import Any

from langchain_core.tools import StructuredTool


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


_registry: dict[str, RoleDef] = {}


def register(role: RoleDef) -> RoleDef:
    _registry[role.name] = role
    return role


def get_role(name: str) -> RoleDef:
    try:
        return _registry[name]
    except KeyError:
        raise KeyError(f"unknown role: {name}") from None


def list_roles() -> list[RoleDef]:
    return list(_registry.values())


def role_names() -> list[str]:
    return sorted(_registry)


def clear_roles() -> None:
    _registry.clear()


def call_role(name: str, query: str) -> str:
    role = get_role(name)
    if role.builder is None:
        raise ValueError(f"role has no builder: {name}")
    subgraph = role.builder()
    result = subgraph.invoke({"messages": [{"role": "user", "content": query}]})
    return str(result["messages"][-1].content)


def role_as_tool(name: str) -> StructuredTool:
    role = get_role(name)

    def _run(query: str) -> str:
        return call_role(name, query)

    return StructuredTool.from_function(
        func=_run,
        name=f"call_{role.name}",
        description=role.description,
    )
