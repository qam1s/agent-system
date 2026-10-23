from __future__ import annotations

from ..domain.entities import McpServer


class InMemoryMcpRegistry:
    def __init__(self) -> None:
        self._servers: dict[str, McpServer] = {}

    def register(self, name: str, description: str = "") -> McpServer:
        server = McpServer(name=name, description=description)
        self._servers[name] = server
        return server

    def list_servers(self) -> list[McpServer]:
        return list(self._servers.values())

    def clear(self) -> None:
        self._servers.clear()

    def tools(self, name: str) -> list[object]:
        if name not in self._servers:
            raise KeyError(f"unknown MCP server: {name}")
        return []
