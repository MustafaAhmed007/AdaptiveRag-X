import math
from collections import Counter

from ..models import Document, Evidence
from .base import Retriever, tokenize


class BM25Retriever(Retriever):
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.docs: list[Document] = []

    def add(self, documents: list[Document]) -> None:
        self.docs.extend(documents)

    def retrieve(self, query: str, top_k: int = 5) -> list[Evidence]:
        if not self.docs:
            return []
        tokenized = [tokenize(doc.text) for doc in self.docs]
        avg_len = sum(map(len, tokenized)) / len(tokenized)
        query_terms = set(tokenize(query))
        df = Counter(term for tokens in tokenized for term in set(tokens))
        scored = []
        for doc, tokens in zip(self.docs, tokenized):
            frequencies = Counter(tokens)
            score = 0.0
            for term in query_terms:
                if term not in frequencies:
                    continue
                idf = math.log(1 + (len(self.docs) - df[term] + 0.5) / (df[term] + 0.5))
                tf = frequencies[term]
                denominator = tf + self.k1 * (1 - self.b + self.b * len(tokens) / max(avg_len, 1))
                score += idf * tf * (self.k1 + 1) / denominator
            normalized = min(1.0, score / 5)
            scored.append((normalized, doc))
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
