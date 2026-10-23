from fastapi import APIRouter, Header

from ..application.dto import ChatInput
from ..application.interactors import ChatInteractor
from .schemas import ChatIn, ChatOut


def create_chat_router(interactor: ChatInteractor) -> APIRouter:
    router = APIRouter()

    @router.post("/chat", response_model=ChatOut)
    def chat(
        body: ChatIn,
        idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    ):
        out = interactor(
            ChatInput(message=body.message, thread_id=body.thread_id),
            idempotency_key=idempotency_key,
        )
        return ChatOut(thread_id=out.thread_id, reply=out.reply)

    @router.get("/health")
    def health():
        return {"ok": True}

    return router
