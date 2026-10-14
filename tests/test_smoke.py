from fastapi.testclient import TestClient
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig

from agent_system.gateway import app
from agent_system.graph import graph


def test_chat_thread_continues():
    c = TestClient(app)
    r1 = c.post("/chat", json={"message": "hello"}).json()
    assert r1["reply"] == "researcher: hello"
    r2 = c.post("/chat", json={"message": "again", "thread_id": r1["thread_id"]}).json()
    assert r2["thread_id"] == r1["thread_id"]
    assert r2["reply"] == "researcher: again"
    state = graph.get_state(config={"configurable": {"thread_id": r1["thread_id"]}})
    assert len(state.values["messages"]) == 4


def test_idempotency_key_replays():
    c = TestClient(app)
    headers = {"Idempotency-Key": "test-key-1"}
    a = c.post("/chat", json={"message": "m1"}, headers=headers).json()
    b = c.post("/chat", json={"message": "other"}, headers=headers).json()
    assert a == b


async def test_stream_modes():
    config: RunnableConfig = {"configurable": {"thread_id": "test-stream"}}
    msgs = [
        chunk
        async for chunk in graph.astream(
            {"messages": [HumanMessage(content="hi")]},
            config=config,
            stream_mode="messages",
        )
    ]
    vals = [
        chunk
        async for chunk in graph.astream(
            {"messages": [HumanMessage(content="hi2")]},
            config=config,
            stream_mode="values",
        )
    ]
    assert msgs
    assert vals and "messages" in vals[-1]
