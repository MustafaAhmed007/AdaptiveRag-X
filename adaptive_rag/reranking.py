from .models import Evidence


class CrossEncoderReranker:
    """Optional sentence-transformers cross-encoder reranker."""

    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        from sentence_transformers import CrossEncoder

        self.model = CrossEncoder(model_name)

    def rerank(self, query: str, evidence: list[Evidence], top_k: int = 5) -> list[Evidence]:
        pairs = [(query, item.text) for item in evidence]
        scores = self.model.predict(pairs)
        ranked = sorted(zip(scores, evidence), key=lambda item: float(item[0]), reverse=True)
        return [
            item.model_copy(update={"score": max(0.0, min(1.0, (float(score) + 1) / 2)), "rank": index})
            for index, (score, item) in enumerate(ranked[:top_k], start=1)
        ]
