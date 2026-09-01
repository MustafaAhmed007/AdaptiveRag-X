import hashlib
import math
from abc import ABC, abstractmethod


class Embedder(ABC):
    @abstractmethod
    def embed(self, text: str) -> list[float]:
        raise NotImplementedError


class HashEmbedder(Embedder):
    """Deterministic, dependency-free embedding for local tests and demos."""

    def __init__(self, dimensions: int = 128):
        self.dimensions = dimensions

    def embed(self, text: str) -> list[float]:
        values = [0.0] * self.dimensions
        tokens = text.lower().split()
        for token in tokens:
            digest = hashlib.sha256(token.encode()).digest()
            index = int.from_bytes(digest[:4], "big") % self.dimensions
            values[index] += 1.0
        norm = math.sqrt(sum(value * value for value in values)) or 1.0
        return [value / norm for value in values]


class OpenAIEmbedder(Embedder):
    def __init__(self, client, model: str = "text-embedding-3-small"):
        self.client = client
        self.model = model

    def embed(self, text: str) -> list[float]:
        response = self.client.embeddings.create(model=self.model, input=text)
        return list(response.data[0].embedding)
