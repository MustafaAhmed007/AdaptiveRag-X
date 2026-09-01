from ..embeddings import Embedder
from ..models import Document, Evidence
from .base import Retriever


class QdrantRetriever(Retriever):
    """Optional production vector adapter; requires qdrant-client."""

    def __init__(self, client, collection: str, embedder: Embedder):
        self.client = client
        self.collection = collection
        self.embedder = embedder

    def add(self, documents: list[Document]) -> None:
        from qdrant_client.models import PointStruct, VectorParams

        try:
            self.client.get_collection(self.collection)
        except Exception:
            vector = self.embedder.embed("dimension probe")
            self.client.create_collection(
                collection_name=self.collection,
                vectors_config=VectorParams(size=len(vector), distance="Cosine"),
            )
        points = [
            PointStruct(
                id=doc.id,
                vector=self.embedder.embed(doc.text),
                payload={"text": doc.text, "source": doc.source, "metadata": doc.metadata},
            )
            for doc in documents
        ]
        self.client.upsert(collection_name=self.collection, points=points)

    def retrieve(self, query: str, top_k: int = 5) -> list[Evidence]:
        hits = self.client.query_points(
            collection_name=self.collection,
            query=self.embedder.embed(query),
            limit=top_k,
            with_payload=True,
        ).points
        return [
            Evidence(
                document_id=str(hit.id),
                text=hit.payload.get("text", ""),
                score=max(0.0, min(1.0, float(hit.score))),
                source=hit.payload.get("source", "qdrant"),
                rank=index,
                metadata=hit.payload.get("metadata", {}),
            )
            for index, hit in enumerate(hits, start=1)
        ]
