from .base import Retriever, Reranker
from ..models import Evidence

class SimpleReranker(Reranker):
    def rerank(self, query: str, evidence: list[Evidence], k: int = 5) -> list[Evidence]:
        q = set(query.lower().split())
        def score(e: Evidence) -> float:
            words = set(e.text.lower().split())
            lexical = len(q & words) / max(len(q), 1)
            return 0.6 * e.score + 0.4 * lexical
        ranked = sorted(evidence, key=score, reverse=True)
        return [e.model_copy(update={"score": min(score(e), 1.0)}) for e in ranked[:k]]

class HybridRetriever(Retriever):
    """Combines two retrieval signals through normalized weighted fusion."""
    def __init__(self, dense: Retriever, sparse: Retriever, alpha: float = 0.65):
        if not 0 <= alpha <= 1:
            raise ValueError("alpha must be between 0 and 1")
        self.dense, self.sparse, self.alpha = dense, sparse, alpha

    def retrieve(self, query: str, k: int = 5) -> list[Evidence]:
        dense = self.dense.retrieve(query, k * 2)
        sparse = self.sparse.retrieve(query, k * 2)
        by_id: dict[str, Evidence] = {}
        for item in dense:
            by_id[item.document_id] = item.model_copy(update={"score": self.alpha * item.score})
        for item in sparse:
            if item.document_id in by_id:
                old = by_id[item.document_id]
                score = old.score + (1 - self.alpha) * item.score
                by_id[item.document_id] = old.model_copy(update={"score": score})
            else:
                by_id[item.document_id] = item.model_copy(update={"score": (1 - self.alpha) * item.score})
        return sorted(by_id.values(), key=lambda x: x.score, reverse=True)[:k]
