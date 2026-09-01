from abc import ABC, abstractmethod
from collections import Counter
import re

from ..models import Document, Evidence


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def lexical_score(query: str, text: str) -> float:
    query_terms = Counter(tokenize(query))
    text_terms = Counter(tokenize(text))
    if not query_terms:
        return 0.0
    overlap = sum(min(query_terms[token], text_terms[token]) for token in query_terms)
    return min(1.0, overlap / sum(query_terms.values()))


class Retriever(ABC):
    @abstractmethod
    def add(self, documents: list[Document]) -> None:
        raise NotImplementedError

    @abstractmethod
    def retrieve(self, query: str, top_k: int = 5) -> list[Evidence]:
        raise NotImplementedError
