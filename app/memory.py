"""Durable, branch-capable local conversation storage."""

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
import sqlite3
from uuid import uuid4


@dataclass(frozen=True)
class Message:
    role: str
    content: str


class ConversationStore:
    def __init__(self, max_messages: int, database_path: str = ":memory:") -> None:
        self._max_messages = max_messages
        if database_path != ":memory:":
            Path(database_path).parent.mkdir(parents=True, exist_ok=True)
        self._db = sqlite3.connect(database_path, check_same_thread=False)
        self._db.row_factory = sqlite3.Row
        self._db.executescript("""
            PRAGMA foreign_keys = ON;
            CREATE TABLE IF NOT EXISTS conversations (
              id TEXT PRIMARY KEY, title TEXT NOT NULL, title_is_manual INTEGER NOT NULL DEFAULT 0,
              created_at TEXT NOT NULL, updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS messages (
              id TEXT PRIMARY KEY, conversation_id TEXT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
              parent_message_id TEXT REFERENCES messages(id), role TEXT NOT NULL, content TEXT NOT NULL,
              model TEXT, is_active INTEGER NOT NULL DEFAULT 1, created_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS messages_conversation ON messages(conversation_id, created_at);
        """)
        self._db.commit()

    @staticmethod
    def _now() -> str:
        return datetime.now(UTC).isoformat()

    def _ensure(self, conversation_id: str, first_message: str = "New conversation") -> None:
        now = self._now()
        self._db.execute("INSERT OR IGNORE INTO conversations VALUES (?, ?, 0, ?, ?)", (conversation_id, first_message, now, now))

    def history(self, conversation_id: str) -> list[Message]:
        rows = self._db.execute("SELECT role, content FROM messages WHERE conversation_id = ? AND is_active = 1 ORDER BY created_at", (conversation_id,)).fetchall()
        return [Message(row["role"], row["content"]) for row in rows[-self._max_messages :]]

    def add_turn(self, conversation_id: str, user_message: str, assistant_message: str, model: str | None = None) -> None:
        self._ensure(conversation_id, self._title_from(user_message))
        parent = self._db.execute("SELECT id FROM messages WHERE conversation_id = ? AND is_active = 1 ORDER BY created_at DESC LIMIT 1", (conversation_id,)).fetchone()
        parent_id = parent["id"] if parent else None
        user_id, assistant_id, now = str(uuid4()), str(uuid4()), self._now()
        self._db.execute("INSERT INTO messages VALUES (?, ?, ?, 'user', ?, NULL, 1, ?)", (user_id, conversation_id, parent_id, user_message, now))
        self._db.execute("INSERT INTO messages VALUES (?, ?, ?, 'assistant', ?, ?, 1, ?)", (assistant_id, conversation_id, user_id, assistant_message, model, now))
        self._db.execute("UPDATE conversations SET updated_at = ? WHERE id = ?", (now, conversation_id))
        self._db.commit()

    def add_branch(self, conversation_id: str, parent_message_id: str | None, user_message: str, assistant_message: str, model: str | None = None) -> None:
        """Select a new child at a parent without deleting the previous branch."""
        self._ensure(conversation_id, self._title_from(user_message))
        self._db.execute("UPDATE messages SET is_active = 0 WHERE conversation_id = ? AND parent_message_id IS ?", (conversation_id, parent_message_id))
        user_id, assistant_id, now = str(uuid4()), str(uuid4()), self._now()
        self._db.execute("INSERT INTO messages VALUES (?, ?, ?, 'user', ?, NULL, 1, ?)", (user_id, conversation_id, parent_message_id, user_message, now))
        self._db.execute("INSERT INTO messages VALUES (?, ?, ?, 'assistant', ?, ?, 1, ?)", (assistant_id, conversation_id, user_id, assistant_message, model, now))
        self._db.execute("UPDATE conversations SET updated_at = ? WHERE id = ?", (now, conversation_id)); self._db.commit()

    @staticmethod
    def _title_from(message: str) -> str:
        words = message.strip().split()
        return " ".join(words[:8])[:80] or "New conversation"

    def list(self) -> list[dict[str, str]]:
        rows = self._db.execute("SELECT id, title, updated_at FROM conversations ORDER BY updated_at DESC").fetchall()
        return [dict(row) for row in rows]

    def get(self, conversation_id: str) -> dict[str, object] | None:
        row = self._db.execute("SELECT id, title FROM conversations WHERE id = ?", (conversation_id,)).fetchone()
        if not row: return None
        return {"id": row["id"], "title": row["title"], "messages": [message.__dict__ for message in self.history(conversation_id)]}

    def rename(self, conversation_id: str, title: str) -> bool:
        result = self._db.execute("UPDATE conversations SET title = ?, title_is_manual = 1, updated_at = ? WHERE id = ?", (title, self._now(), conversation_id))
        self._db.commit(); return result.rowcount > 0

    def clear(self, conversation_id: str) -> None:
        self._db.execute("DELETE FROM conversations WHERE id = ?", (conversation_id,)); self._db.commit()
