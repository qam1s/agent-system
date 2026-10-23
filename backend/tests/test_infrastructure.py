from back.application.dto import ChatOutput
from back.domain.entities import RoleDef
from back.infrastructure.memory_audit import InMemoryAuditWriter
from back.infrastructure.memory_idempotency import InMemoryIdempotencyStore
from back.infrastructure.researcher import register_researcher
from back.infrastructure.role_registry import InMemoryRoleRegistry


def test_memory_audit_writer_roundtrip():
    audit = InMemoryAuditWriter()
    record = audit.write("t1", "researcher", "role_call", {"query": "q"})

    assert record.thread_id == "t1"
    assert record.at
    assert len(audit.list_records()) == 1
    audit.clear()
    assert audit.list_records() == []


def test_memory_idempotency_store_roundtrip():
    store = InMemoryIdempotencyStore()
    assert store.get("missing") is None

    out = ChatOutput(thread_id="t1", reply="r1")
    store.put("k1", out)

    assert store.get("k1") == out


def test_role_registry_call_and_tool():
    registry = InMemoryRoleRegistry()
    register_researcher(registry)

    assert "researcher" in registry.names()
    reply = registry("researcher", "q1")

    assert reply == "researcher: q1"
    tool = registry.as_tool("researcher")

    assert tool.name == "call_researcher"
    assert tool.invoke({"query": "q2"}) == "researcher: q2"


def test_role_registry_unknown_role():
    registry = InMemoryRoleRegistry()
    try:
        registry.get("nope")
    except KeyError as exc:
        assert "unknown role" in str(exc)
    else:
        raise AssertionError("expected KeyError")

    try:
        registry.register(RoleDef(name="empty", description="d", system_prompt="s"))
        registry("empty", "q")
    except ValueError as exc:
        assert "no builder" in str(exc)
    else:
        raise AssertionError("expected ValueError")
