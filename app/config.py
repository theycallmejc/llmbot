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
        )

