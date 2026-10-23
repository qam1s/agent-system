from back.application.dto import ChatInput
from back.application.interactors import ChatInteractor
from back.infrastructure.memory_idempotency import InMemoryIdempotencyStore


class FakeRunner:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    def run(self, message: str, thread_id: str) -> str:
        self.calls.append((message, thread_id))
        return f"reply:{message}"


def test_chat_interactor_generates_thread_and_replies():
    runner = FakeRunner()
    store = InMemoryIdempotencyStore()
    interactor = ChatInteractor(runner=runner, idempotency=store)

    out = interactor(ChatInput(message="hello"))

    assert out.thread_id
    assert out.reply == "reply:hello"
    assert runner.calls[0][0] == "hello"


def test_chat_interactor_replays_idempotency_key():
    runner = FakeRunner()
    store = InMemoryIdempotencyStore()
    interactor = ChatInteractor(runner=runner, idempotency=store)

    first = interactor(ChatInput(message="m1"), idempotency_key="k1")
    second = interactor(ChatInput(message="other"), idempotency_key="k1")

    assert first == second
    assert len(runner.calls) == 1


def test_chat_interactor_keeps_explicit_thread():
    runner = FakeRunner()
    store = InMemoryIdempotencyStore()
    interactor = ChatInteractor(runner=runner, idempotency=store)

    out = interactor(ChatInput(message="hi", thread_id="t-1"))

    assert out.thread_id == "t-1"
    assert runner.calls[0] == ("hi", "t-1")
