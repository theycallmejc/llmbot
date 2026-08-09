"""Conversation orchestration: prompt, remembered context, then provider call."""

from app.memory import ConversationStore, Message
from app.provider import ChatProvider


class BotService:
    def __init__(self, provider: ChatProvider, store: ConversationStore, system_prompt: str) -> None:
        self._provider, self._store, self._system_prompt = provider, store, system_prompt

    async def reply(self, conversation_id: str, user_message: str) -> str:
        messages = [Message("system", self._system_prompt), *self._store.history(conversation_id), Message("user", user_message)]
        reply = await self._provider.complete(messages)
        self._store.add_turn(conversation_id, user_message, reply)
        return reply

    def clear(self, conversation_id: str) -> None:
        self._store.clear(conversation_id)

