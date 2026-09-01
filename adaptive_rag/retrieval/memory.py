from ..models import Document, Evidence
from .base import Retriever, lexical_score


class InMemoryRetriever(Retriever):
    def __init__(self, documents: list[Document] | None = None):
        self.docs = list(documents or [])

    def add(self, documents: list[Document]) -> None:
        self.docs.extend(documents)

    def retrieve(self, query: str, top_k: int = 5) -> list[Evidence]:
        scored = [(lexical_score(query, doc.text), doc) for doc in self.docs]
        scored.sort(key=lambda item: item[0], reverse=True)
        return [
            Evidence(
                document_id=doc.id,
                text=doc.text,
                score=score,
                source=doc.source,
                rank=index,
                metadata=doc.metadata,
            )
            for index, (score, doc) in enumerate(scored[:top_k], start=1)
            if score > 0
        ]


class InMemoryDenseLike(InMemoryRetriever):
    """Compatibility/local dense-like retriever using deterministic lexical features."""
