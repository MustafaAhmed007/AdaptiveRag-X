from ..models import Document, Evidence
from .base import Retriever, lexical_score

class InMemoryRetriever(Retriever):
    """Deterministic local retriever used for development and tests."""
    def __init__(self, documents: list[Document] | None = None):
        self.documents = documents or []

    def add(self, document: Document) -> None:
        self.documents.append(document)

    def retrieve(self, query: str, k: int = 5) -> list[Evidence]:
        ranked = sorted(
            self.documents,
            key=lambda d: lexical_score(query, d.text),
            reverse=True,
        )
        return [
            Evidence(document_id=d.id, text=d.text, score=lexical_score(query, d.text), source=d.source)
            for d in ranked[:k]
            if lexical_score(query, d.text) > 0
        ]
