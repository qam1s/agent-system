from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph

from ..application.interfaces import AuditWriter, RoleRunner
from ..application.state import AgentState, Context
from .checkpointer import get_checkpointer

DEFAULT_ROLE = "researcher"


def create_supervisor(
    roles: RoleRunner, audit: AuditWriter, default_role: str = DEFAULT_ROLE
):
    def supervisor(
        state: AgentState, config: RunnableConfig
    ) -> dict[str, list[AIMessage]]:
        last = state["messages"][-1].content if state["messages"] else ""
        reply = roles(default_role, str(last))
        thread_id = str((config.get("configurable") or {}).get("thread_id", ""))
        audit.write(
            thread_id, default_role, "role_call", {"query": str(last), "reply": reply}
        )
        return {"messages": [AIMessage(content=reply)]}

    return supervisor


def build_graph(
    checkpointer=None,
    roles: RoleRunner | None = None,
    audit: AuditWriter | None = None,
    default_role: str = DEFAULT_ROLE,
):
    from .memory_audit import InMemoryAuditWriter
    from .researcher import register_researcher
    from .role_registry import InMemoryRoleRegistry

    if roles is None:
        registry = InMemoryRoleRegistry()
        register_researcher(registry)
        effective_roles: RoleRunner = registry
    else:
        effective_roles = roles
    if audit is None:
        audit = InMemoryAuditWriter()
    supervisor = create_supervisor(effective_roles, audit, default_role)
    builder = StateGraph(AgentState, context_schema=Context)  # ty: ignore[invalid-argument-type]
    builder.add_node("supervisor", supervisor)
    builder.add_edge(START, "supervisor")
    builder.add_edge("supervisor", END)
    return builder.compile(checkpointer=checkpointer or get_checkpointer())
