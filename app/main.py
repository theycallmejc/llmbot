"""HTTP entrypoint for the standalone bot."""

from pathlib import Path
from uuid import uuid4
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.config import Settings
from app.errors import BotError
from app.memory import ConversationStore
from app.provider import OpenAICompatibleProvider
from app.service import BotService


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=12_000)
    conversation_id: str | None = Field(default=None, max_length=100)


class ChatResponse(BaseModel):
    message: str
    conversation_id: str
    model: str


def create_app(service: BotService | None = None, settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings.from_environment()
    service = service or BotService(OpenAICompatibleProvider(settings.api_key, settings.model, settings.base_url, settings.timeout_seconds), ConversationStore(settings.max_history_messages), settings.system_prompt)
    app = FastAPI(title="Chat Bot", version="1.0.0")

    @app.exception_handler(BotError)
    async def bot_error(_: Request, error: BotError) -> JSONResponse:
        return JSONResponse(
            status_code=error.status_code,
            content={"error": {"code": error.code, "message": error.message}},
        )

    @app.get("/api/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/api/chat", response_model=ChatResponse)
    async def chat(request: ChatRequest) -> ChatResponse:
        message = request.message.strip()
        if not message:
            raise HTTPException(422, "message must not be blank")
        conversation_id = request.conversation_id or str(uuid4())
        return ChatResponse(message=await service.reply(conversation_id, message), conversation_id=conversation_id, model=settings.model)

    @app.delete("/api/conversations/{conversation_id}", status_code=204)
    async def clear_conversation(conversation_id: str) -> Response:
        service.clear(conversation_id)
        return Response(status_code=204)

    static_dir = Path(__file__).parent / "static"
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    app.get("/", include_in_schema=False)(lambda: FileResponse(static_dir / "index.html"))
    return app


app = create_app()
