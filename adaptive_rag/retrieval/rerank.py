from ..models import Evidence
from .base import tokenize


class ScoreReranker:
    def rerank(self, query: str, evidence: list[Evidence], top_k: int = 5) -> list[Evidence]:
        query_terms = set(tokenize(query))

        def score(item: Evidence) -> float:
            overlap = len(query_terms & set(tokenize(item.text))) / max(len(query_terms), 1)
            return min(1.0, 0.65 * item.score + 0.35 * overlap)

        ranked = sorted(evidence, key=score, reverse=True)[:top_k]
        return [
            item.model_copy(update={"score": score(item), "rank": index})
            for index, item in enumerate(ranked, start=1)
        ]


SimpleReranker = ScoreReranker
