from adaptive_rag.models import Document
from adaptive_rag.retrieval.memory import InMemoryRetriever
from adaptive_rag.retrieval.hybrid import HybridRetriever, SimpleReranker

def test_memory_retriever_ranks_matching_document():
    r = InMemoryRetriever([
        Document(id="a", text="python web api"),
        Document(id="b", text="database indexing"),
    ])
    results = r.retrieve("python api", 2)
    assert results[0].document_id == "a"

def test_hybrid_fuses_duplicate_candidates():
    a = InMemoryRetriever([Document(id="a", text="python api")])
    b = InMemoryRetriever([Document(id="a", text="python service")])
    results = HybridRetriever(a, b).retrieve("python", 1)
    assert results[0].document_id == "a"

def test_reranker_keeps_top_k():
    r = SimpleReranker()
    evidence = InMemoryRetriever([Document(id="a", text="python api")]).retrieve("python")
    assert len(r.rerank("python", evidence, 1)) == 1
