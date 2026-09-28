from ..embeddings import Embedder
from ..models import Document, Evidence
from .base import Retriever


class QdrantRetriever(Retriever):
    """Optional production vector adapter with tenant-isolated retrieval."""

    def __init__(self, client, collection: str, embedder: Embedder):
        self.client = client
        self.collection = collection
        self.embedder = embedder

    def add(self, documents: list[Document]) -> None:
        from qdrant_client.http.exceptions import UnexpectedResponse
        from qdrant_client.models import Distance, PointStruct, VectorParams

        try:
            self.client.get_collection(self.collection)
        except UnexpectedResponse as exc:
            if getattr(exc, "status_code", None) != 404:
                raise

            vector = self.embedder.embed("dimension probe")

            self.client.create_collection(
                collection_name=self.collection,
                vectors_config=VectorParams(
                    size=len(vector),
                    distance=Distance.COSINE,
                ),
            )

        points = [
            PointStruct(
                id=doc.id,
                vector=self.embedder.embed(doc.text),
                payload={
                    "text": doc.text,
                    "source": doc.source,
                    "metadata": doc.metadata,
                    "tenant_id": doc.tenant_id,
                },
            )
            for doc in documents
        ]

        self.client.upsert(
            collection_name=self.collection,
            points=points,
        )

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        tenant_id: str = "default",
    ) -> list[Evidence]:
        from qdrant_client.models import FieldCondition, Filter, MatchValue

        tenant_filter = Filter(
            must=[
                FieldCondition(
                    key="tenant_id",
                    match=MatchValue(value=tenant_id),
                )
            ]
        )

        hits = self.client.query_points(
            collection_name=self.collection,
            query=self.embedder.embed(query),
            query_filter=tenant_filter,
            limit=top_k,
            with_payload=True,
        ).points

        results = []

        for index, hit in enumerate(hits, start=1):
            payload = hit.payload or {}

            results.append(
                Evidence(
                    document_id=str(hit.id),
                    text=payload.get("text", ""),
                    score=max(0.0, min(1.0, float(hit.score))),
                    source=payload.get("source", "qdrant"),
                    rank=index,
                    metadata=payload.get("metadata", {}),
                )
            )

        return results