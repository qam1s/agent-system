from dataclasses import dataclass


@dataclass
class ChatInput:
    message: str
    thread_id: str | None = None


@dataclass
class ChatOutput:
    thread_id: str
    reply: str
