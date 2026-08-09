"""Bounded, in-memory conversation storage."""

from collections import defaultdict
from dataclasses import dataclass


@dataclass(frozen=True)
class Message:
    role: str
    content: str


class ConversationStore:
    def __init__(self, max_messages: int) -> None:
        self._max_messages = max_messages
        self._conversations: dict[str, list[Message]] = defaultdict(list)

    def history(self, conversation_id: str) -> list[Message]:
        return list(self._conversations[conversation_id])

    def add_turn(self, conversation_id: str, user_message: str, assistant_message: str) -> None:
        messages = self._conversations[conversation_id]
        messages.extend((Message("user", user_message), Message("assistant", assistant_message)))
        self._conversations[conversation_id] = messages[-self._max_messages :]

    def clear(self, conversation_id: str) -> None:
        self._conversations.pop(conversation_id, None)

