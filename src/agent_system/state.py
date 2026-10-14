from typing import TypedDict

from langgraph.graph import MessagesState


class Context(TypedDict, total=False):
    user_id: str
    tenant_id: str


class AgentState(MessagesState):
    pass
