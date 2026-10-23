from typing import Any

from fastapi.testclient import TestClient
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig

from back.config import AppConfig
from back.ioc import create_container, get_app


def make_client(monkeypatch) -> tuple[TestClient, Any]:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    container = create_container(AppConfig(database_url="", default_role="researcher"))
    return TestClient(get_app(container)), container.graph


def test_chat_thread_continues(monkeypatch):
    client, graph = make_client(monkeypatch)
    r1 = client.post("/chat", json={"message": "how does the checkpointer work"}).json()
    assert "[S1]" in r1["reply"]
    r2 = client.post(
        "/chat", json={"message": "again", "thread_id": r1["thread_id"]}
    ).json()
    assert r2["thread_id"] == r1["thread_id"]
    assert "abstain" in r2["reply"]
    state = graph.get_state(config={"configurable": {"thread_id": r1["thread_id"]}})
    assert len(state.values["messages"]) == 4


def test_idempotency_key_replays(monkeypatch):
    client, _ = make_client(monkeypatch)
    headers = {"Idempotency-Key": "test-key-1"}
    a = client.post("/chat", json={"message": "m1"}, headers=headers).json()
    b = client.post("/chat", json={"message": "other"}, headers=headers).json()
    assert a == b


async def test_stream_modes(monkeypatch):
    _, graph = make_client(monkeypatch)
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
