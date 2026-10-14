from langchain_core.messages import AIMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph


def supervisor_stub(state: MessagesState) -> dict[str, list[AIMessage]]:
    last = state["messages"][-1].content if state["messages"] else ""
    return {"messages": [AIMessage(content=f"stub: {last}")]}


def build_graph():
    builder = StateGraph(MessagesState)  # ty: ignore[invalid-argument-type]
    builder.add_node("supervisor", supervisor_stub)
    builder.add_edge(START, "supervisor")
    builder.add_edge("supervisor", END)
    return builder.compile(checkpointer=InMemorySaver())


graph = build_graph()
