from abc import ABC, abstractmethod
from ..models import Document, Evidence

class Retriever(ABC):
    @abstractmethod
    def retrieve(self, query: str, k: int = 5) -> list[Evidence]: ...

class Reranker(ABC):
    @abstractmethod
    def rerank(self, query: str, evidence: list[Evidence], k: int = 5) -> list[Evidence]: ...


def lexical_score(query: str, text: str) -> float:
    q = set(query.lower().split())
    t = set(text.lower().split())
    if not q or not t:
        return 0.0
    return len(q & t) / len(q)
