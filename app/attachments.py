"""Safe local text-file attachment storage and extraction."""
from pathlib import Path
from uuid import uuid4
from fastapi import UploadFile

ALLOWED_SUFFIXES = {".txt", ".md", ".json", ".csv", ".log", ".yaml", ".yml", ".py", ".js", ".html", ".css"}

class AttachmentError(ValueError): pass

class AttachmentStore:
    def __init__(self, root: str, max_bytes: int = 1_000_000) -> None:
        self.root, self.max_bytes = Path(root), max_bytes; self.root.mkdir(parents=True, exist_ok=True)

    async def save(self, upload: UploadFile) -> dict[str, str]:
        name = Path(upload.filename or "").name
        suffix = Path(name).suffix.lower()
        if not name or suffix not in ALLOWED_SUFFIXES: raise AttachmentError("That file type is not supported.")
        data = await upload.read(self.max_bytes + 1)
        if len(data) > self.max_bytes: raise AttachmentError("The file is larger than the 1 MB limit.")
        try: text = data.decode("utf-8")
        except UnicodeDecodeError as error: raise AttachmentError("The file must be UTF-8 text.") from error
        attachment_id = str(uuid4()); (self.root / f"{attachment_id}{suffix}").write_text(text, encoding="utf-8")
        return {"id": attachment_id, "name": name, "content": text}
