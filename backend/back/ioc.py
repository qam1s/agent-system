from dataclasses import dataclass
from typing import Any

from fastapi import FastAPI

from .application.interactors import ChatInteractor
from .config import AppConfig
from .controllers.http import create_chat_router
from .infrastructure.checkpointer import get_checkpointer
from .infrastructure.conversation_runner import GraphConversationRunner
from .infrastructure.langgraph_graph import build_graph
from .infrastructure.mcp_registry import InMemoryMcpRegistry
from .infrastructure.memory_audit import InMemoryAuditWriter
from .infrastructure.memory_idempotency import InMemoryIdempotencyStore
from .infrastructure.researcher import register_researcher
from .infrastructure.role_registry import InMemoryRoleRegistry


@dataclass
class AppContainer:
    config: AppConfig
    audit: InMemoryAuditWriter
    idempotency: InMemoryIdempotencyStore
    roles: InMemoryRoleRegistry
    mcps: InMemoryMcpRegistry
    graph: Any
    interactor: ChatInteractor


def create_container(config: AppConfig | None = None) -> AppContainer:
    cfg = config or AppConfig.from_env()
    audit = InMemoryAuditWriter()
    idempotency = InMemoryIdempotencyStore()
    roles = InMemoryRoleRegistry()
    register_researcher(roles)
    mcps = InMemoryMcpRegistry()
    graph = build_graph(
        checkpointer=get_checkpointer(cfg.database_url),
        roles=roles,
        audit=audit,
        default_role=cfg.default_role,
    )
    runner = GraphConversationRunner(graph)
    interactor = ChatInteractor(runner=runner, idempotency=idempotency)
    return AppContainer(
        config=cfg,
        audit=audit,
        idempotency=idempotency,
        roles=roles,
        mcps=mcps,
        graph=graph,
        interactor=interactor,
    )


def get_app(container: AppContainer | None = None) -> FastAPI:
    container = container or create_container()
    app = FastAPI(title="agent-system")
    app.include_router(create_chat_router(container.interactor))
    app.state.container = container
    return app
