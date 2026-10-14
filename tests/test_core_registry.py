from langgraph.checkpoint.memory import InMemorySaver

from agent_system import researcher as _researcher  # noqa: F401
from agent_system.audit import clear_audits, list_audits, write_audit
from agent_system.checkpoint import get_checkpointer, reset_checkpointer_cache
from agent_system.mcp import clear_mcps, get_mcp_tools, list_mcps, register_mcp
from agent_system.roles import call_role, get_role, role_as_tool, role_names


def test_researcher_registered():
    assert "researcher" in role_names()
    role = get_role("researcher")
    assert role.builder is not None
    assert (
        "prompt_id" not in role.system_prompt or "researcher/v0" in role.system_prompt
    )


def test_role_call_returns_final_message_only():
    reply = call_role("researcher", "deep question")
    assert reply == "researcher: deep question"
    assert isinstance(reply, str)


def test_role_as_tool_returns_final_message_only():
    tool = role_as_tool("researcher")
    assert tool.name == "call_researcher"
    result = tool.invoke({"query": "q1"})
    assert result == "researcher: q1"


def test_audit_writer_stub():
    clear_audits()
    record = write_audit("t1", "researcher", "role_call", {"query": "q"})
    assert record.thread_id == "t1"
    assert record.at
    assert len(list_audits()) == 1


def test_mcp_registry_stub():
    clear_mcps()
    register_mcp("docs", "documentation server")
    assert [s.name for s in list_mcps()] == ["docs"]
    assert get_mcp_tools("docs") == []


def test_checkpointer_defaults_to_inmemory(monkeypatch):
    reset_checkpointer_cache()
    monkeypatch.delenv("DATABASE_URL", raising=False)
    checkpointer = get_checkpointer()
    assert isinstance(checkpointer, InMemorySaver)
