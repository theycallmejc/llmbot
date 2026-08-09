"""Small local lexical retriever for uploaded text documents."""
from pathlib import Path
import re

def _terms(text: str) -> set[str]: return set(re.findall(r"[a-z0-9]{2,}", text.lower()))

class LocalRetriever:
    def __init__(self, root: str) -> None: self.root = Path(root)
    def search(self, query: str, limit: int = 4) -> list[dict[str, str]]:
        wanted = _terms(query); found = []
        for path in self.root.glob("*"):
            if not path.is_file(): continue
            for index, chunk in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines()):
                score = len(wanted & _terms(chunk))
                if score: found.append((score, path.stem, index + 1, chunk[:1200]))
        return [{"document_id": doc, "line": str(line), "content": content} for _, doc, line, content in sorted(found, reverse=True)[:limit]]
