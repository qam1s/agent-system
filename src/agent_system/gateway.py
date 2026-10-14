import uuid

from fastapi import FastAPI, Header
from langchain_core.messages import HumanMessage
from pydantic import BaseModel

from .graph import graph

app = FastAPI(title="agent-system smoke")


class ChatIn(BaseModel):
    message: str
    thread_id: str | None = None


class ChatOut(BaseModel):
    thread_id: str
    reply: str


_idempotency: dict[str, ChatOut] = {}


@app.post("/chat", response_model=ChatOut)
def chat(
    body: ChatIn,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
):
    if idempotency_key and idempotency_key in _idempotency:
        return _idempotency[idempotency_key]
    thread_id = body.thread_id or str(uuid.uuid4())
    result = graph.invoke(
        {"messages": [HumanMessage(content=body.message)]},
        config={"configurable": {"thread_id": thread_id}},
    )
    out = ChatOut(thread_id=thread_id, reply=str(result["messages"][-1].content))
    if idempotency_key:
        _idempotency[idempotency_key] = out
    return out


@app.get("/health")
def health():
    return {"ok": True}
