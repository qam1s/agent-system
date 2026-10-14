from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph

from . import researcher as _researcher  # noqa: F401
from .audit import write_audit
from .checkpoint import get_checkpointer
from .roles import call_role
from .state import AgentState, Context

DEFAULT_ROLE = "researcher"


def supervisor(state: AgentState, config: RunnableConfig) -> dict[str, list[AIMessage]]:
    last = state["messages"][-1].content if state["messages"] else ""
    reply = call_role(DEFAULT_ROLE, str(last))
    thread_id = str((config.get("configurable") or {}).get("thread_id", ""))
    write_audit(
        thread_id, DEFAULT_ROLE, "role_call", {"query": str(last), "reply": reply}
    )
    return {"messages": [AIMessage(content=reply)]}


def build_graph(checkpointer=None):
    builder = StateGraph(AgentState, context_schema=Context)  # ty: ignore[invalid-argument-type]
    builder.add_node("supervisor", supervisor)
    builder.add_edge(START, "supervisor")
    builder.add_edge("supervisor", END)
    return builder.compile(checkpointer=checkpointer or get_checkpointer())


graph = build_graph()
