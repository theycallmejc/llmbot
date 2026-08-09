"""HTTP entrypoint for the standalone bot."""

from pathlib import Path
from uuid import uuid4
from fastapi import FastAPI, HTTPException, Request, Response, UploadFile, Query
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
import json
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.config import Settings
from app.context import ContextBuilder
from app.attachments import AttachmentError, AttachmentStore
from app.retrieval import LocalRetriever
from app.tools import ToolError, execute
from app.governance import RequestGuard
from app.errors import BotError
from app.memory import ConversationStore
from app.provider import OpenAICompatibleProvider
from app.prompts import assemble
from app.service import BotService


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=12_000)
    conversation_id: str | None = Field(default=None, max_length=100)


class ChatResponse(BaseModel):
    message: str
    conversation_id: str
    model: str


class RenameRequest(BaseModel):
    title: str = Field(min_length=1, max_length=100)

class ToolRequest(BaseModel):
    name: str = Field(max_length=50)
    arguments: dict[str, str]


def create_app(service: BotService | None = None, settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings.from_environment()
    primary = OpenAICompatibleProvider(settings.api_key, settings.model, settings.base_url, settings.timeout_seconds)
    fallback = OpenAICompatibleProvider(settings.api_key, settings.fallback_model, settings.base_url, settings.timeout_seconds) if settings.fallback_model else None
    prompt = assemble(domain_instructions=settings.domain_instructions)
    system_prompt = settings.system_prompt if settings.system_prompt != "You are a helpful, concise assistant." else prompt.text
    service = service or BotService(primary, ConversationStore(settings.max_history_messages, settings.database_path), system_prompt, fallback, ContextBuilder(settings.max_context_tokens), RequestGuard(settings.requests_per_minute, settings.requests_per_day))
    app = FastAPI(title="Chat Bot", version="1.0.0")
    attachments = AttachmentStore(settings.attachment_path)
    retriever = LocalRetriever(settings.attachment_path)

    @app.exception_handler(BotError)
    async def bot_error(_: Request, error: BotError) -> JSONResponse:
        return JSONResponse(
            status_code=error.status_code,
            content={"error": {"code": error.code, "message": error.message}},
        )

    @app.get("/api/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/api/attachments")
    async def upload_attachment(file: UploadFile) -> dict[str, str]:
        try: return await attachments.save(file)
        except AttachmentError as error: raise HTTPException(422, str(error)) from error

    @app.get("/api/retrieval")
    async def retrieve(query: str = Query(min_length=2, max_length=500)) -> dict[str, object]:
        return {"sources": retriever.search(query)}

    @app.post("/api/tools")
    async def run_tool(request: ToolRequest) -> dict[str, object]:
        try: return execute(request.name, request.arguments)
        except ToolError as error: raise HTTPException(422, str(error)) from error

    @app.post("/api/chat", response_model=ChatResponse)
    async def chat(request: ChatRequest) -> ChatResponse:
        message = request.message.strip()
        if not message:
            raise HTTPException(422, "message must not be blank")
        conversation_id = request.conversation_id or str(uuid4())
        return ChatResponse(message=await service.reply(conversation_id, message), conversation_id=conversation_id, model=settings.model)

    @app.post("/api/chat/stream")
    async def stream_chat(request: ChatRequest) -> StreamingResponse:
        message = request.message.strip()
        if not message: raise HTTPException(422, "message must not be blank")
        conversation_id = request.conversation_id or str(uuid4())
        async def events():
            try:
                async for chunk in service.stream_reply(conversation_id, message):
                    yield f"event: chunk\ndata: {json.dumps({'text': chunk})}\n\n"
                yield f"event: done\ndata: {json.dumps({'conversation_id': conversation_id, 'model': settings.model})}\n\n"
            except BotError as error:
                yield f"event: error\ndata: {json.dumps({'message': error.message})}\n\n"
        return StreamingResponse(events(), media_type="text/event-stream", headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

    @app.delete("/api/conversations/{conversation_id}", status_code=204)
    async def clear_conversation(conversation_id: str) -> Response:
        service.clear(conversation_id)
        return Response(status_code=204)

    @app.get("/api/conversations")
    async def conversations() -> list[dict[str, str]]:
        return service.list_conversations()

    @app.get("/api/conversations/{conversation_id}")
    async def conversation(conversation_id: str) -> dict[str, object]:
        result = service.get_conversation(conversation_id)
        if not result: raise HTTPException(404, "conversation not found")
        return result

    @app.patch("/api/conversations/{conversation_id}")
    async def rename_conversation(conversation_id: str, request: RenameRequest) -> Response:
        if not service.rename(conversation_id, request.title.strip()): raise HTTPException(404, "conversation not found")
        return Response(status_code=204)

    static_dir = Path(__file__).parent / "static"
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    app.get("/", include_in_schema=False)(lambda: FileResponse(static_dir / "index.html"))
    return app


app = create_app()
