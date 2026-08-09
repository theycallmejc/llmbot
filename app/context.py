"""Deterministic context selection for local conversations."""

from app.memory import Message


class ContextBuilder:
    def __init__(self, max_tokens: int) -> None:
        self._max_tokens = max_tokens

    @staticmethod
    def estimate_tokens(message: Message) -> int:
        return max(1, (len(message.content) + 3) // 4)

    def build(self, system_prompt: str, history: list[Message], latest: Message) -> list[Message]:
        selected = [latest]
        budget = self._max_tokens - self.estimate_tokens(Message("system", system_prompt)) - self.estimate_tokens(latest)
        for message in reversed(history):
            cost = self.estimate_tokens(message)
            if cost > budget: break
            selected.insert(0, message); budget -= cost
        return [Message("system", system_prompt), *selected]
