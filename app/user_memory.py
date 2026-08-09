"""Explicit, local-only user memory; never auto-saves chat content."""
import sqlite3
from uuid import uuid4

class MemoryStore:
    def __init__(self, database_path: str) -> None:
        self.db = sqlite3.connect(database_path, check_same_thread=False)
        self.db.execute("CREATE TABLE IF NOT EXISTS user_memory (id TEXT PRIMARY KEY, content TEXT NOT NULL)"); self.db.commit()
    def add(self, content: str) -> dict[str, str]:
        item = {"id": str(uuid4()), "content": content}; self.db.execute("INSERT INTO user_memory VALUES (?, ?)", tuple(item.values())); self.db.commit(); return item
    def list(self) -> list[dict[str, str]]:
        return [{"id": row[0], "content": row[1]} for row in self.db.execute("SELECT id, content FROM user_memory")]
    def delete(self, memory_id: str) -> None:
        self.db.execute("DELETE FROM user_memory WHERE id = ?", (memory_id,)); self.db.commit()
