from langchain_core.messages import AIMessage
from langgraph.graph import END, START, StateGraph

from ..application.research_pipeline import (
    abstain_report,
    check_report,
    clarify_report,
    decide_route,
    draft_report,
    make_plan,
    revise_report,
    search_sources,
)
from ..application.state import AgentState
from ..domain.entities import Hit, RoleDef, Route
from .corpus import get_seed_sources
from .role_registry import InMemoryRoleRegistry

PROMPT_ID = "researcher/v0"
SYSTEM_PROMPT = (
    f"researcher stub (prompt_id={PROMPT_ID}): plan→search→report with citations"
)


class ResearcherState(AgentState):
    query: str
    route: Route
    plan: list[str]
    hits: list[Hit]
    draft: str
    attempts: int
    report: str


def router_node(state: ResearcherState) -> dict:
    query = str(state["messages"][-1].content) if state["messages"] else ""
    return {"query": query, "route": decide_route(query)}


def route_next(state: ResearcherState) -> str:
    return "clarify" if state["route"]["confidence"] < 0.5 else "plan"


def clarify_node(state: ResearcherState) -> dict:
    return {
        "report": clarify_report(),
        "messages": [AIMessage(content=clarify_report())],
    }


def plan_node(state: ResearcherState) -> dict:
    return {"plan": make_plan(state["query"])}


def retrieve_node(state: ResearcherState) -> dict:
    return {"hits": search_sources(get_seed_sources(), state["query"])}


def report_node(state: ResearcherState) -> dict:
    hits = state["hits"]
    if hits:
        draft = draft_report(state["query"], state["plan"], hits)
    else:
        draft = abstain_report(state["query"])
    return {"draft": draft, "attempts": 0}


def gate_next(state: ResearcherState) -> str:
    verdict = check_report(state["draft"], state["hits"])
    if verdict["passed"]:
        return "finalize"
    if state["attempts"] < 1:
        return "revise"
    return "fallback"


def revise_node(state: ResearcherState) -> dict:
    revised = revise_report(state["query"], state["plan"], state["hits"])
    return {"draft": revised, "attempts": state["attempts"] + 1}


def fallback_node(state: ResearcherState) -> dict:
    return {"report": abstain_report(state["query"])}


def finalize_node(state: ResearcherState) -> dict:
    report = state.get("report", state["draft"])
    return {"report": report, "messages": [AIMessage(content=report)]}


def build_researcher():
    builder = StateGraph(ResearcherState)  # ty: ignore[invalid-argument-type]
    builder.add_node("router", router_node)
    builder.add_node("clarify", clarify_node)
    builder.add_node("plan", plan_node)
    builder.add_node("retrieve", retrieve_node)
    builder.add_node("report", report_node)
    builder.add_node("revise", revise_node)
    builder.add_node("fallback", fallback_node)
    builder.add_node("finalize", finalize_node)
    builder.add_edge(START, "router")
    builder.add_conditional_edges(
        "router", route_next, {"clarify": "clarify", "plan": "plan"}
    )
    builder.add_edge("clarify", END)
    builder.add_edge("plan", "retrieve")
    builder.add_edge("retrieve", "report")
    builder.add_conditional_edges(
        "report",
        gate_next,
        {"finalize": "finalize", "revise": "revise", "fallback": "fallback"},
    )
    builder.add_conditional_edges(
        "revise",
        gate_next,
        {"finalize": "finalize", "revise": "revise", "fallback": "fallback"},
    )
    builder.add_edge("fallback", "finalize")
    builder.add_edge("finalize", END)
    return builder.compile()


def register_researcher(registry: InMemoryRoleRegistry) -> RoleDef:
    return registry.register(
        RoleDef(
            name="researcher",
            description="plan→search→report with citations; abstains on no-hit",
            system_prompt=SYSTEM_PROMPT,
            builder=build_researcher,
        )
    )
