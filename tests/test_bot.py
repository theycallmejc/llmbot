import asyncio

import httpx
from fastapi.testclient import TestClient

from app.config import Settings
from app.memory import ConversationStore, Message
from app.provider import OpenAICompatibleProvider
from app.service import BotService
from app.main import create_app


class FakeProvider:
    def __init__(self) -> None:
        self.calls: list[list[Message]] = []

    async def complete(self, messages: list[Message]) -> str:
        self.calls.append(messages)
        return "Hello from the bot"


def make_client() -> tuple[TestClient, FakeProvider]:
    provider = FakeProvider()
    settings = Settings(None, "test-model", "https://example.test/v1", "Be helpful", 1, 4)
    service = BotService(provider, ConversationStore(4), settings.system_prompt)
    return TestClient(create_app(service, settings)), provider


def test_chat_creates_a_conversation_and_remembers_it() -> None:
    client, provider = make_client()
    first = client.post("/api/chat", json={"message": "First"})
    conversation_id = first.json()["conversation_id"]
    second = client.post("/api/chat", json={"message": "Second", "conversation_id": conversation_id})
    assert first.status_code == second.status_code == 200
    assert second.json()["conversation_id"] == conversation_id
    assert [message.content for message in provider.calls[1]] == ["Be helpful", "First", "Hello from the bot", "Second"]


def test_blank_chat_is_rejected() -> None:
    client, _ = make_client()
    assert client.post("/api/chat", json={"message": "  "}).status_code == 422


def test_conversation_can_be_cleared() -> None:
    client, provider = make_client()
    conversation_id = client.post("/api/chat", json={"message": "First"}).json()["conversation_id"]
    assert client.delete(f"/api/conversations/{conversation_id}").status_code == 204
    client.post("/api/chat", json={"message": "Second", "conversation_id": conversation_id})
    assert [message.content for message in provider.calls[-1]] == ["Be helpful", "Second"]


def test_openai_compatible_provider_returns_model_content() -> None:
    transport = httpx.MockTransport(
        lambda request: httpx.Response(
            200,
            request=request,
            json={"choices": [{"message": {"content": " Provider reply "}}]},
        )
    )
    provider = OpenAICompatibleProvider("test-key", "test-model", "https://example.test/v1", 1, transport)

    response = asyncio.run(provider.complete([Message("user", "Hello")]))

    assert response == "Provider reply"
