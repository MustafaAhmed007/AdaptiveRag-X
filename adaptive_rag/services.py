from pathlib import Path
from uuid import uuid4

from .models import Document


def chunk_text(text: str, size: int = 800, overlap: int = 120) -> list[str]:
    if size <= overlap:
        raise ValueError("size must exceed overlap")
    words = text.split()
    width = max(1, size // 5)
    step = max(1, width - overlap // 5)
    chunks = []
    start = 0
    while start < len(words):
        chunks.append(" ".join(words[start : start + width]))
        if start + width >= len(words):
            break
        start += step
    return [chunk for chunk in chunks if chunk.strip()]


def ingest_text(text: str, source: str = "upload", metadata: dict | None = None, tenant_id: str = "default") -> list[Document]:
    return [
        Document(id=str(uuid4()), text=chunk, source=source, metadata=metadata or {}, tenant_id=tenant_id)
        for chunk in chunk_text(text)
    ]


def ingest_markdown(text: str, source: str = "markdown", tenant_id: str = "default") -> list[Document]:
    sections = text.split("\n# ")
    return [
        Document(
            id=str(uuid4()),
            text=section.strip(),
            source=source,
            metadata={"format": "markdown"},
            tenant_id=tenant_id,
        )
        for section in sections
        if section.strip()
    ]


def load_file(path: str, tenant_id: str = "default") -> list[Document]:
    file_path = Path(path)
    suffix = file_path.suffix.lower()
    if suffix not in {".txt", ".md", ".markdown"}:
        raise ValueError("supported file types are .txt, .md and .markdown")
    text = file_path.read_text(encoding="utf-8")
    return ingest_markdown(text, str(file_path), tenant_id) if suffix in {".md", ".markdown"} else ingest_text(text, str(file_path), tenant_id=tenant_id)
