from langchain_core.messages import AIMessage
from langgraph.graph import END, START, StateGraph

from .roles import RoleDef, register, role_names
from .state import AgentState

PROMPT_ID = "researcher/v0"
SYSTEM_PROMPT = (
    f"researcher stub (prompt_id={PROMPT_ID}): plan→search→report with citations"
)


def researcher_node(state: AgentState) -> dict[str, list[AIMessage]]:
    last = state["messages"][-1].content if state["messages"] else ""
    return {"messages": [AIMessage(content=f"researcher: {last}")]}


def build_researcher():
    builder = StateGraph(AgentState)  # ty: ignore[invalid-argument-type]
    builder.add_node("researcher", researcher_node)
    builder.add_edge(START, "researcher")
    builder.add_edge("researcher", END)
    return builder.compile()


def register_researcher() -> RoleDef:
    return register(
        RoleDef(
            name="researcher",
            description="plan→search→report with citations; abstains on no-hit",
            system_prompt=SYSTEM_PROMPT,
            builder=build_researcher,
        )
    )


if "researcher" not in role_names():
    register_researcher()
