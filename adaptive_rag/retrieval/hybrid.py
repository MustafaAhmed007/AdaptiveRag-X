from .base import Retriever
from .rerank import ScoreReranker


class HybridRetriever(Retriever):
    def __init__(self, dense, sparse, dense_weight: float = 0.6, sparse_weight: float = 0.4):
        self.dense = dense
        self.sparse = sparse
        self.dw = dense_weight
        self.sw = sparse_weight

    def add(self, documents) -> None:
        self.dense.add(documents)
        self.sparse.add(documents)

    def retrieve(self, query: str, top_k: int = 5):
        results = {}
        for item in self.dense.retrieve(query, top_k * 2):
            results[item.document_id] = item.model_copy(update={"score": self.dw * item.score})
        for item in self.sparse.retrieve(query, top_k * 2):
            if item.document_id in results:
                old = results[item.document_id]
                results[item.document_id] = old.model_copy(
                    update={"score": old.score + self.sw * item.score}
                )
            else:
                results[item.document_id] = item.model_copy(update={"score": self.sw * item.score})
        ranked = sorted(results.values(), key=lambda item: item.score, reverse=True)
        return [item.model_copy(update={"rank": index}) for index, item in enumerate(ranked[:top_k], 1)]


SimpleReranker = ScoreReranker
__all__ = ["HybridRetriever", "SimpleReranker"]
