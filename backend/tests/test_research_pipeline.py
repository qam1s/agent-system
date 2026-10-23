from back.application.research_pipeline import (
    abstain_report,
    check_report,
    clarify_report,
    decide_route,
    draft_report,
    make_plan,
    revise_report,
    search_sources,
)
from back.domain.entities import Source
from back.infrastructure.corpus import get_seed_sources
from back.infrastructure.researcher import build_researcher

SOURCES = get_seed_sources()


def test_router_routes_and_clarifies():
    assert decide_route("how does the checkpointer work") == {
        "role": "researcher",
        "confidence": 1.0,
    }
    assert decide_route("   ") == {"role": "", "confidence": 0.0}


def test_plan_mentions_query_terms():
    plan = make_plan("how does the checkpointer work")

    assert len(plan) == 3
    assert "checkpointer" in plan[0]


def test_search_hits_and_no_hit():
    hits = search_sources(SOURCES, "how does the checkpointer work")

    assert hits and hits[0]["id"] == "S1"
    assert search_sources(SOURCES, "hello") == []


def test_draft_carries_citations_and_sources():
    hits = search_sources(SOURCES, "tell me about roles")
    draft = draft_report("tell me about roles", ["step"], hits)

    assert "[S2]" in draft
    assert "Sources:" in draft
    assert check_report(draft, hits) == {"passed": True, "issues": []}


def test_gate_rejects_unknown_citations():
    hits = search_sources(SOURCES, "tell me about roles")
    verdict = check_report("claim [S9]", hits)

    assert not verdict["passed"]
    assert verdict["issues"]


def test_gate_requires_abstain_without_sources():
    assert check_report("some report", [])["passed"] is False
    assert check_report(abstain_report("hello"), [])["passed"] is True


def test_revise_recovers_or_abstains():
    hits = search_sources(SOURCES, "tell me about the gateway")
    revised = revise_report("tell me about the gateway", ["step"], hits)

    assert check_report(revised, hits)["passed"] is True
    assert "abstain" in revise_report("hello", ["step"], [])


def test_subgraph_reports_citations():
    graph = build_researcher()
    result = graph.invoke({"messages": [{"role": "user", "content": "what are roles"}]})

    assert "[S2]" in str(result["messages"][-1].content)


def test_subgraph_abstains_and_clarifies():
    graph = build_researcher()
    no_hit = graph.invoke({"messages": [{"role": "user", "content": "hello"}]})
    empty = graph.invoke({"messages": [{"role": "user", "content": "   "}]})

    assert "abstain" in str(no_hit["messages"][-1].content)
    assert "clarify" in str(empty["messages"][-1].content)
    assert "clarify" in clarify_report()


def test_seed_corpus_has_expected_sources():
    assert [source.id for source in SOURCES] == ["S1", "S2", "S3", "S4"]
    assert all(isinstance(source, Source) for source in SOURCES)
