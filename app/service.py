"""Conversation orchestration: prompt, remembered context, then provider call."""

from app.memory import ConversationStore, Message
from app.context import ContextBuilder
from app.provider import ChatProvider
from collections.abc import AsyncIterator


class BotService:
    def __init__(self, provider: ChatProvider, store: ConversationStore, system_prompt: str, fallback_provider: ChatProvider | None = None, context_builder: ContextBuilder | None = None) -> None:
        self._provider, self._store, self._system_prompt, self._fallback_provider = provider, store, system_prompt, fallback_provider
        self._context_builder = context_builder or ContextBuilder(6000)

    async def reply(self, conversation_id: str, user_message: str) -> str:
        messages = self._context_builder.build(self._system_prompt, self._store.history(conversation_id), Message("user", user_message))
        try:
            reply = await self._provider.complete(messages)
        except Exception:
            if not self._fallback_provider: raise
            reply = await self._fallback_provider.complete(messages)
        self._store.add_turn(conversation_id, user_message, reply)
        return reply

    async def stream_reply(self, conversation_id: str, user_message: str) -> AsyncIterator[str]:
        messages = self._context_builder.build(self._system_prompt, self._store.history(conversation_id), Message("user", user_message))
        parts: list[str] = []
        async for chunk in self._provider.stream(messages):
            parts.append(chunk); yield chunk
        reply = "".join(parts).strip()
        if reply: self._store.add_turn(conversation_id, user_message, reply)

    def clear(self, conversation_id: str) -> None:
        self._store.clear(conversation_id)

    def list_conversations(self) -> list[dict[str, str]]:
        return self._store.list()

    def get_conversation(self, conversation_id: str) -> dict[str, object] | None:
        return self._store.get(conversation_id)

    def rename(self, conversation_id: str, title: str) -> bool:
        return self._store.rename(conversation_id, title)
