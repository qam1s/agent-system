from langchain_core.messages import HumanMessage

from ..application.interfaces import ConversationRunner


class GraphConversationRunner(ConversationRunner):
    def __init__(self, graph) -> None:
        self._graph = graph

    def run(self, message: str, thread_id: str) -> str:
        result = self._graph.invoke(
            {"messages": [HumanMessage(content=message)]},
            config={"configurable": {"thread_id": thread_id}},
        )
        return str(result["messages"][-1].content)
