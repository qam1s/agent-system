from fastapi.testclient import TestClient

from back.config import AppConfig
from back.ioc import create_container, get_app


def make_client(monkeypatch) -> TestClient:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    container = create_container(AppConfig(database_url="", default_role="researcher"))
    return TestClient(get_app(container))


def test_chat_controller_replies(monkeypatch):
    client = make_client(monkeypatch)
    response = client.post("/chat", json={"message": "how does the checkpointer work"})

    assert response.status_code == 200
    body = response.json()
    assert "[S1]" in body["reply"]
    assert body["thread_id"]


def test_chat_controller_abstains_on_no_hit(monkeypatch):
    client = make_client(monkeypatch)
    body = client.post("/chat", json={"message": "hello"}).json()

    assert "abstain" in body["reply"]


def test_chat_controller_idempotent(monkeypatch):
    client = make_client(monkeypatch)
    headers = {"Idempotency-Key": "controller-key-1"}

    first = client.post("/chat", json={"message": "m1"}, headers=headers).json()
    second = client.post("/chat", json={"message": "other"}, headers=headers).json()

    assert first == second


def test_health_controller(monkeypatch):
    client = make_client(monkeypatch)

    assert client.get("/health").json() == {"ok": True}
