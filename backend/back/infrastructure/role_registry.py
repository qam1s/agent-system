from __future__ import annotations

from langchain_core.tools import StructuredTool

from ..domain.entities import RoleDef


class InMemoryRoleRegistry:
    def __init__(self) -> None:
        self._roles: dict[str, RoleDef] = {}

    def register(self, role: RoleDef) -> RoleDef:
        self._roles[role.name] = role
        return role

    def get(self, name: str) -> RoleDef:
        try:
            return self._roles[name]
        except KeyError:
            raise KeyError(f"unknown role: {name}") from None

    def list_roles(self) -> list[RoleDef]:
        return list(self._roles.values())

    def names(self) -> list[str]:
        return sorted(self._roles)

    def clear(self) -> None:
        self._roles.clear()

    def __call__(self, role: str, query: str) -> str:
        role_def = self.get(role)
        if role_def.builder is None:
            raise ValueError(f"role has no builder: {role}")
        subgraph = role_def.builder()
        result = subgraph.invoke({"messages": [{"role": "user", "content": query}]})
        return str(result["messages"][-1].content)

    def as_tool(self, name: str) -> StructuredTool:
        role_def = self.get(name)

        def _run(query: str) -> str:
            return self(role_def.name, query)

        return StructuredTool.from_function(
            func=_run,
            name=f"call_{role_def.name}",
            description=role_def.description,
        )
