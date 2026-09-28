from types import SimpleNamespace

from adaptive_rag.embeddings import HashEmbedder
from adaptive_rag.models import Document
from adaptive_rag.retrieval.qdrant import QdrantRetriever


class FakeQdrantClient:
    def __init__(self):
        self.query_arguments = None
        self.points = [
            SimpleNamespace(
                id="doc-a",
                score=0.95,
                payload={
                    "text": "Tenant A secret",
                    "source": "test",
                    "metadata": {},
                    "tenant_id": "tenant-a",
                },
            )
        ]

    def query_points(self, **kwargs):
        self.query_arguments = kwargs
        return SimpleNamespace(points=self.points)


def test_qdrant_retrieve_applies_tenant_filter():
    client = FakeQdrantClient()

    retriever = QdrantRetriever(
        client=client,
        collection="test",
        embedder=HashEmbedder(),
    )

    results = retriever.retrieve(
        query="secret",
        top_k=5,
        tenant_id="tenant-a",
    )

    assert len(results) == 1
    assert results[0].document_id == "doc-a"

    query_filter = client.query_arguments["query_filter"]

    assert len(query_filter.must) == 1

    condition = query_filter.must[0]

    assert condition.key == "tenant_id"
    assert condition.match.value == "tenant-a"


def test_qdrant_add_preserves_tenant_id():
    class ExistingCollectionClient(FakeQdrantClient):
        def get_collection(self, collection):
            return SimpleNamespace()

        def upsert(self, **kwargs):
            self.upsert_arguments = kwargs

    client = ExistingCollectionClient()

    retriever = QdrantRetriever(
        client=client,
        collection="test",
        embedder=HashEmbedder(),
    )

    document = Document(
        id="doc-a",
        text="Tenant A secret",
        source="test",
        tenant_id="tenant-a",
    )

    retriever.add([document])

    payload = client.upsert_arguments["points"][0].payload

    assert payload["tenant_id"] == "tenant-a"