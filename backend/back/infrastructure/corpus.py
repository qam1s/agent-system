from ..domain.entities import Source

SEED_SOURCES: list[Source] = [
    Source(
        id="S1",
        title="Checkpointer",
        text=(
            "The top-level graph compiles with a checkpointer. "
            "It uses InMemorySaver by default and switches to PostgresSaver "
            "when DATABASE_URL is set. Per-thread state enables resume and streaming."
        ),
    ),
    Source(
        id="S2",
        title="Roles",
        text=(
            "Roles are named autonomous agents in a registry. "
            "The catalog holds researcher, support, analyst, coder, sre, reviewer. "
            "Each role is directly invocable and callable as a tool by other agents."
        ),
    ),
    Source(
        id="S3",
        title="Gateway",
        text=(
            "POST /chat accepts a message and an optional thread_id with "
            "an Idempotency-Key header. Replies return thread_id and reply, "
            "and threads continue across calls."
        ),
    ),
    Source(
        id="S4",
        title="Researcher pipeline",
        text=(
            "The researcher role runs router, plan, retrieve, report, quality gate. "
            "The retriever abstains on no-hit and every claim carries a citation."
        ),
    ),
]


def get_seed_sources() -> list[Source]:
    return list(SEED_SOURCES)
