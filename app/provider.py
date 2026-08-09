"""Small adapter for OpenAI-compatible chat-completions APIs."""

from collections.abc import AsyncIterator
import json
from typing import Protocol
import httpx

from app.errors import BotError, ConfigurationError, RateLimitError
from app.memory import Message


class ChatProvider(Protocol):
    async def complete(self, messages: list[Message]) -> str: ...
    async def stream(self, messages: list[Message]) -> AsyncIterator[str]: ...


class OpenAICompatibleProvider:
    def __init__(self, api_key: str | None, model: str, base_url: str, timeout_seconds: float, transport: httpx.AsyncBaseTransport | None = None) -> None:
        self._api_key, self._model, self._base_url = api_key, model, base_url
        self._timeout_seconds, self._transport = timeout_seconds, transport

    async def complete(self, messages: list[Message]) -> str:
        if not self._api_key:
            raise ConfigurationError()
        try:
            async with httpx.AsyncClient(base_url=self._base_url, timeout=self._timeout_seconds, transport=self._transport) as client:
                response = await client.post("/chat/completions", headers={"Authorization": f"Bearer {self._api_key}"}, json={"model": self._model, "messages": [message.__dict__ for message in messages]})
        except httpx.HTTPError as error:
            raise BotError() from error
        if response.status_code == 429:
            raise RateLimitError()
        if response.is_error:
            raise BotError()
        try:
            content = response.json()["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError, ValueError) as error:
            raise BotError() from error
        if not isinstance(content, str) or not content.strip():
            raise BotError()
        return content.strip()

    async def stream(self, messages: list[Message]) -> AsyncIterator[str]:
        if not self._api_key: raise ConfigurationError()
        try:
            async with httpx.AsyncClient(base_url=self._base_url, timeout=self._timeout_seconds, transport=self._transport) as client:
                async with client.stream("POST", "/chat/completions", headers={"Authorization": f"Bearer {self._api_key}"}, json={"model": self._model, "messages": [m.__dict__ for m in messages], "stream": True}) as response:
                    if response.status_code == 429: raise RateLimitError()
                    if response.is_error: raise BotError()
                    async for line in response.aiter_lines():
                        if not line.startswith("data: "): continue
                        payload = line[6:]
                        if payload == "[DONE]": return
                        try: content = json.loads(payload)["choices"][0]["delta"].get("content", "")
                        except (KeyError, IndexError, TypeError, ValueError): continue
                        if content: yield content
        except httpx.HTTPError as error:
            raise BotError() from error
