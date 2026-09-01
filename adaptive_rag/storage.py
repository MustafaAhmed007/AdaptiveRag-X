import sqlite3
from abc import ABC, abstractmethod

from .models import Document


class DocumentStore(ABC):
    @abstractmethod
    def upsert(self, documents: list[Document]) -> None:
        raise NotImplementedError

    @abstractmethod
    def list(self, tenant_id: str = "default") -> list[Document]:
        raise NotImplementedError

    @abstractmethod
    def delete(self, document_id: str, tenant_id: str = "default") -> None:
        raise NotImplementedError


class SQLiteDocumentStore(DocumentStore):
    def __init__(self, path: str = "adaptive_rag.db"):
        self.path = path
        with sqlite3.connect(self.path) as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS documents "
                "(id TEXT PRIMARY KEY, text TEXT NOT NULL, source TEXT, "
                "metadata TEXT, tenant_id TEXT NOT NULL, version INTEGER NOT NULL)"
            )

    def upsert(self, documents: list[Document]) -> None:
        import json

        with sqlite3.connect(self.path) as conn:
            conn.executemany(
                "INSERT OR REPLACE INTO documents VALUES (?, ?, ?, ?, ?, ?)",
                [
                    (d.id, d.text, d.source, json.dumps(d.metadata), d.tenant_id, d.version)
                    for d in documents
                ],
            )

    def list(self, tenant_id: str = "default") -> list[Document]:
        import json

        with sqlite3.connect(self.path) as conn:
            rows = conn.execute(
                "SELECT id,text,source,metadata,tenant_id,version FROM documents WHERE tenant_id=?",
                (tenant_id,),
            ).fetchall()
        return [
            Document(
                id=row[0],
                text=row[1],
                source=row[2] or "memory",
                metadata=json.loads(row[3] or "{}"),
                tenant_id=row[4],
                version=row[5],
            )
            for row in rows
        ]

    def delete(self, document_id: str, tenant_id: str = "default") -> None:
        with sqlite3.connect(self.path) as conn:
            conn.execute("DELETE FROM documents WHERE id=? AND tenant_id=?", (document_id, tenant_id))
