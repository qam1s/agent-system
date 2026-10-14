from dataclasses import dataclass
from typing import Any


@dataclass
class McpServer:
    name: str
    description: str = ""


_servers: dict[str, McpServer] = {}


def register_mcp(name: str, description: str = "") -> McpServer:
    server = McpServer(name=name, description=description)
    _servers[name] = server
    return server


def list_mcps() -> list[McpServer]:
    return list(_servers.values())


def clear_mcps() -> None:
    _servers.clear()


def get_mcp_tools(name: str) -> list[Any]:
    if name not in _servers:
        raise KeyError(f"unknown MCP server: {name}")
    return []
