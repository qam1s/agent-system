import re

from ..domain.entities import GateVerdict, Hit, Route, Source

_WORD = re.compile(r"[a-z0-9]+")
_CITATION = re.compile(r"\[([A-Za-z0-9]+)\]")

STOPWORDS = frozenset(
    {
        "how",
        "does",
        "what",
        "why",
        "when",
        "where",
        "which",
        "who",
        "the",
        "and",
        "for",
        "with",
        "from",
        "into",
        "about",
        "tell",
        "please",
        "is",
        "are",
        "was",
        "were",
        "has",
        "have",
        "had",
        "not",
        "but",
        "you",
        "can",
        "could",
        "would",
        "should",
        "there",
        "their",
        "them",
        "then",
        "than",
        "that",
        "this",
        "these",
        "those",
        "will",
        "just",
        "like",
        "get",
        "got",
        "all",
        "any",
        "our",
        "your",
    }
)


def tokenize(text: str) -> set[str]:
    return {w for w in _WORD.findall(text.lower()) if len(w) >= 3} - STOPWORDS


def decide_route(query: str) -> Route:
    if not query.strip():
        return {"role": "", "confidence": 0.0}
    return {"role": "researcher", "confidence": 1.0}


def make_plan(query: str) -> list[str]:
    terms = sorted(tokenize(query))
    scope = ", ".join(terms[:5]) or "general"
    return [
        f"identify key terms: {scope}",
        "retrieve sources",
        "draft report with citations",
    ]


def search_sources(sources: list[Source], query: str, top_k: int = 3) -> list[Hit]:
    terms = tokenize(query)
    scored: list[Hit] = []
    for source in sources:
        score = len(terms & tokenize(f"{source.title} {source.text}"))
        if score > 0:
            scored.append(
                {
                    "id": source.id,
                    "title": source.title,
                    "text": source.text,
                    "score": score,
                }
            )
    scored.sort(key=lambda hit: (-hit["score"], hit["id"]))
    return scored[:top_k]


def first_sentence(text: str) -> str:
    sentence = text.split(". ")[0].strip()
    return sentence if sentence.endswith(".") else f"{sentence}."


def draft_report(query: str, plan: list[str], hits: list[Hit]) -> str:
    lines = [f"Report: {query}", f"Plan: {' → '.join(plan)}"]
    for hit in hits:
        lines.append(f"- {first_sentence(hit['text'])} [{hit['id']}]")
    lines.append("Sources:")
    for hit in hits:
        lines.append(f"[{hit['id']}] {hit['title']}")
    return "\n".join(lines)


def abstain_report(query: str) -> str:
    return f"abstain: no sources found for {query!r}; try rephrasing the question"


def clarify_report() -> str:
    return "clarify: empty query, please restate the question"


def check_report(draft: str, hits: list[Hit]) -> GateVerdict:
    cited = set(_CITATION.findall(draft))
    if not hits:
        if "abstain" in draft.lower():
            return {"passed": True, "issues": []}
        return {"passed": False, "issues": ["no sources but no abstain"]}
    hit_ids = {hit["id"] for hit in hits}
    issues = [f"unknown citation [{citation}]" for citation in sorted(cited - hit_ids)]
    issues += [f"uncited source [{hit_id}]" for hit_id in sorted(hit_ids - cited)]
    return {"passed": not issues, "issues": issues}


def revise_report(query: str, plan: list[str], hits: list[Hit]) -> str:
    rebuilt = draft_report(query, plan, hits) if hits else abstain_report(query)
    if check_report(rebuilt, hits)["passed"]:
        return rebuilt
    return abstain_report(query)
