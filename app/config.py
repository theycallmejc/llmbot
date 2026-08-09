"""Application configuration loaded from environment variables."""

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    api_key: str | None
    model: str
    base_url: str
    system_prompt: str
    timeout_seconds: float
    max_history_messages: int
    database_path: str = "data/chatbot.sqlite3"
    fallback_model: str | None = None
    domain_instructions: str | None = None
    max_context_tokens: int = 6000
    attachment_path: str = "data/attachments"

    @classmethod
    def from_environment(cls) -> "Settings":
        timeout = float(os.getenv("BOT_TIMEOUT_SECONDS", "30"))
        history_limit = int(os.getenv("BOT_MAX_HISTORY_MESSAGES", "12"))
        if timeout <= 0 or history_limit < 1:
            raise ValueError("BOT_TIMEOUT_SECONDS must be positive and BOT_MAX_HISTORY_MESSAGES must be at least 1")
        return cls(
            api_key=os.getenv("OPENAI_API_KEY"),
            model=os.getenv("BOT_MODEL", "gpt-4o-mini"),
            base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/"),
            system_prompt=os.getenv("BOT_SYSTEM_PROMPT", "You are a helpful, concise assistant."),
            timeout_seconds=timeout,
            max_history_messages=history_limit,
            database_path=os.getenv("BOT_DATABASE_PATH", "data/chatbot.sqlite3"),
            fallback_model=os.getenv("BOT_FALLBACK_MODEL") or None,
            domain_instructions=os.getenv("BOT_DOMAIN_INSTRUCTIONS") or None,
            max_context_tokens=int(os.getenv("BOT_MAX_CONTEXT_TOKENS", "6000")),
            attachment_path=os.getenv("BOT_ATTACHMENT_PATH", "data/attachments"),
        )
