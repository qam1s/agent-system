import uuid

from .dto import ChatInput, ChatOutput
from .interfaces import ConversationRunner, IdempotencyStore


class ChatInteractor:
    def __init__(
        self, runner: ConversationRunner, idempotency: IdempotencyStore
    ) -> None:
        self._runner = runner
        self._idempotency = idempotency

    def __call__(
        self, dto: ChatInput, idempotency_key: str | None = None
    ) -> ChatOutput:
        if idempotency_key:
            cached = self._idempotency.get(idempotency_key)
            if cached is not None:
                return cached
        thread_id = dto.thread_id or str(uuid.uuid4())
        reply = self._runner.run(dto.message, thread_id)
        out = ChatOutput(thread_id=thread_id, reply=reply)
        if idempotency_key:
            self._idempotency.put(idempotency_key, out)
        return out
