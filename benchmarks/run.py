"""Small deterministic benchmark for routing and evidence behavior."""
from adaptive_rag.models import Document
from adaptive_rag.pipeline import AdaptivePipeline
from adaptive_rag.retrieval.hybrid import SimpleReranker
from adaptive_rag.retrieval.memory import InMemoryRetriever

CASES = [
    ("What is retrieval augmented generation?", "dense_fast"),
    ("Compare dense retrieval versus hybrid retrieval", "adaptive_hybrid_rerank"),
    ("What is the latest status today?", "web_hybrid"),
]

def main() -> None:
    docs = [Document(id="d1", text="retrieval augmented generation uses external evidence")]
    pipeline = AdaptivePipeline(InMemoryRetriever(docs), SimpleReranker())
    passed = 0
    for query, expected in CASES:
        actual = pipeline.run(query).strategy
        ok = actual == expected
        passed += int(ok)
        print(f"{'PASS' if ok else 'FAIL'} | {query} | expected={expected} actual={actual}")
    print(f"routing_accuracy={passed/len(CASES):.2%}")

if __name__ == "__main__":
    main()
