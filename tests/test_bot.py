import asyncio

import httpx
from fastapi.testclient import TestClient

from app.config import Settings
from app.context import ContextBuilder
from app.errors import BotError
from app.memory import ConversationStore, Message
from app.provider import OpenAICompatibleProvider
from app.prompts import assemble
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


def test_provider_error_is_a_json_api_error() -> None:
    class FailingProvider:
        async def complete(self, _: list[Message]) -> str:
            raise BotError()

    settings = Settings(None, "test-model", "https://example.test/v1", "Be helpful", 1, 4)
    client = TestClient(create_app(BotService(FailingProvider(), ConversationStore(4), settings.system_prompt), settings))

    response = client.post("/api/chat", json={"message": "Hello"})

    assert response.status_code == 502
    assert response.json()["error"]["code"] == "provider_error"


def test_sqlite_conversation_survives_store_restart(tmp_path) -> None:
    database = tmp_path / "chat.sqlite3"
    first = ConversationStore(8, str(database))
    first.add_turn("chat-1", "How are you?", "I am well.", "test-model")
    second = ConversationStore(8, str(database))

    assert second.list()[0]["title"] == "How are you?"
    assert [item.content for item in second.history("chat-1")] == ["How are you?", "I am well."]


def test_store_retains_branch_history_without_showing_inactive_branch(tmp_path) -> None:
    store = ConversationStore(8, str(tmp_path / "chat.sqlite3"))
    store.add_turn("chat-1", "Original", "First answer")
    original = store._db.execute("SELECT id FROM messages WHERE content = 'Original'").fetchone()["id"]
    store.add_branch("chat-1", original, "Edited", "Second answer")

    active = [message.content for message in store.history("chat-1")]
    count = store._db.execute("SELECT COUNT(*) FROM messages WHERE conversation_id = 'chat-1'").fetchone()[0]
    assert active == ["Original", "Edited", "Second answer"]
    assert count == 4


def test_manual_title_is_not_replaced_by_later_messages(tmp_path) -> None:
    store = ConversationStore(8, str(tmp_path / "chat.sqlite3"))
    store.add_turn("chat-1", "A long first message about planning", "Answer")
    assert store.rename("chat-1", "My plan")
    store.add_turn("chat-1", "Another message", "Answer")
    assert store.get("chat-1")["title"] == "My plan"


def test_fallback_provider_handles_primary_failure() -> None:
    class BrokenProvider:
        async def complete(self, _: list[Message]) -> str: raise RuntimeError("offline")
    class BackupProvider:
        async def complete(self, _: list[Message]) -> str: return "Fallback answer"
    service = BotService(BrokenProvider(), ConversationStore(4), "Be helpful", BackupProvider())
    assert asyncio.run(service.reply("chat", "Hello")) == "Fallback answer"


def test_prompt_assembly_is_versioned_and_adds_domain_instructions() -> None:
    prompt = assemble(domain_instructions="Use simple language.")
    assert prompt.name == "local-chat" and prompt.version == "v1"
    assert "Use simple language." in prompt.text


def test_context_builder_keeps_latest_request_within_budget() -> None:
    builder = ContextBuilder(12)
    result = builder.build("System", [Message("user", "old " * 20), Message("assistant", "recent")], Message("user", "latest"))
    assert [message.content for message in result] == ["System", "recent", "latest"]


def test_stream_endpoint_sends_chunks_and_persists_reply() -> None:
    class StreamingProvider:
        async def complete(self, _: list[Message]) -> str: return "unused"
        async def stream(self, _: list[Message]):
            yield "Hello"; yield " world"
    settings = Settings(None, "test", "https://example.test", "System", 1, 4)
    store = ConversationStore(4)
    client = TestClient(create_app(BotService(StreamingProvider(), store, "System"), settings))
    response = client.post("/api/chat/stream", json={"message": "Hi"})
    assert response.status_code == 200 and '"text": "Hello"' in response.text
    assert [message.content for message in store.history(response.text.split('conversation_id": "')[1].split('"')[0])] == ["Hi", "Hello world"]


def test_text_attachment_is_saved_and_extracted(tmp_path) -> None:
    from app.attachments import AttachmentStore
    from starlette.datastructures import UploadFile
    import io
    result = asyncio.run(AttachmentStore(str(tmp_path)).save(UploadFile(io.BytesIO(b"hello"), filename="notes.txt")))
    assert result["name"] == "notes.txt" and result["content"] == "hello"


def test_local_retrieval_returns_matching_source(tmp_path) -> None:
    from app.retrieval import LocalRetriever
    (tmp_path / "document.txt").write_text("FastAPI makes web APIs easy", encoding="utf-8")
    assert LocalRetriever(str(tmp_path)).search("FastAPI API")[0]["document_id"] == "document"


def test_calculator_tool_allows_math_not_code() -> None:
    from app.tools import ToolError, execute
    assert execute("calculator", {"expression": "2 * (3 + 4)"})["result"] == 14
    try: execute("calculator", {"expression": "__import__('os')"})
    except ToolError: pass
    else: raise AssertionError("unsafe expression was accepted")


def test_request_guard_enforces_daily_budget() -> None:
    from app.governance import BudgetError, RequestGuard
    guard = RequestGuard(10, 1); guard.check()
    try: guard.check()
    except BudgetError: pass
    else: raise AssertionError("budget was not enforced")


def test_memory_is_explicit_and_can_be_deleted(tmp_path) -> None:
    from app.user_memory import MemoryStore
    store = MemoryStore(str(tmp_path / "memory.sqlite3")); memory = store.add("Prefer concise answers")
    assert store.list() == [memory]
    store.delete(memory["id"]); assert store.list() == []


def test_readiness_and_request_id_are_available() -> None:
    client, _ = make_client(); response = client.get("/api/ready")
    assert response.json() == {"status": "ready"} and response.headers["X-Request-ID"]


def test_evaluation_cases_are_valid_json() -> None:
    import json
    from pathlib import Path
    cases = json.loads((Path(__file__).parents[1] / "evals" / "cases.json").read_text())
    assert {case["name"] for case in cases} == {"empty_message_rejected", "calculator_safe_math"}


def test_security_headers_prevent_framing_and_sniffing() -> None:
    client, _ = make_client(); response = client.get("/")
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["X-Content-Type-Options"] == "nosniff"
