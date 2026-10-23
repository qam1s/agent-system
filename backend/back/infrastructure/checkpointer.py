import os
from contextlib import ExitStack
from typing import Any

from langgraph.checkpoint.memory import InMemorySaver

_stack = ExitStack()
_postgres: Any | None = None


def get_checkpointer(database_url: str = ""):
    url = database_url.strip() or os.getenv("DATABASE_URL", "").strip()
    if not url:
        return InMemorySaver()
    global _postgres
    if _postgres is None:
        from langgraph.checkpoint.postgres import PostgresSaver

        _postgres = _stack.enter_context(PostgresSaver.from_conn_string(url))
        _postgres.setup()
    return _postgres


def reset_checkpointer_cache() -> None:
    global _postgres
    _postgres = None
