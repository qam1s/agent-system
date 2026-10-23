from pydantic import BaseModel


class ChatIn(BaseModel):
    message: str
    thread_id: str | None = None


class ChatOut(BaseModel):
    thread_id: str
    reply: str
