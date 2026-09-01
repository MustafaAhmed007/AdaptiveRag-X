from collections import defaultdict

from ..models import Document, Evidence
from .base import Retriever, tokenize


class EntityGraphRetriever(Retriever):
    """Lightweight entity graph for multi-hop local retrieval without a graph DB."""

    def __init__(self, documents: list[Document] | None = None):
        self.docs: dict[str, Document] = {}
        self.edges: dict[str, set[str]] = defaultdict(set)
        if documents:
            self.add(documents)

    def add(self, documents: list[Document]) -> None:
        for document in documents:
            self.docs[document.id] = document
        ids = list(self.docs)
        token_sets = {key: set(tokenize(doc.text)) for key, doc in self.docs.items()}
        for index, left in enumerate(ids):
            for right in ids[index + 1 :]:
                overlap = len(token_sets[left] & token_sets[right])
                if overlap >= 2:
                    self.edges[left].add(right)
                    self.edges[right].add(left)

    def retrieve(self, query: str, top_k: int = 5) -> list[Evidence]:
        query_tokens = set(tokenize(query))
        scored = []
        for doc_id, doc in self.docs.items():
            score = len(query_tokens & set(tokenize(doc.text))) / max(len(query_tokens), 1)
            neighbor_bonus = min(0.2, 0.05 * len(self.edges[doc_id]))
            if score > 0:
                scored.append((min(1.0, score + neighbor_bonus), doc))
        scored.sort(key=lambda item: item[0], reverse=True)
        return [
            Evidence(
                document_id=doc.id,
                text=doc.text,
                score=score,
                source="entity-graph",
                rank=index,
                metadata={**doc.metadata, "neighbors": len(self.edges[doc.id])},
            )
            for index, (score, doc) in enumerate(scored[:top_k], start=1)
        ]
