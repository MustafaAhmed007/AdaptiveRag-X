from adaptive_rag.models import Document
from adaptive_rag.retrieval.hybrid import HybridRetriever, SimpleReranker
from adaptive_rag.retrieval.memory import InMemoryRetriever


def test_memory_retriever_ranks_matching_document():
    retriever = InMemoryRetriever(
        [Document(id="a", text="python web api"), Document(id="b", text="database indexing")]
    )
    results = retriever.retrieve("python api", 2)
    assert results[0].document_id == "a"


def test_hybrid_fuses_duplicate_candidates():
    dense = InMemoryRetriever([Document(id="a", text="python api")])
    sparse = InMemoryRetriever([Document(id="a", text="python service")])
    results = HybridRetriever(dense, sparse).retrieve("python", 1)
    assert results[0].document_id == "a"


def test_reranker_keeps_top_k():
    reranker = SimpleReranker()
    evidence = InMemoryRetriever([Document(id="a", text="python api")]).retrieve("python")
    assert len(reranker.rerank("python", evidence, 1)) == 1
