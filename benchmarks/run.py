"""Deterministic smoke benchmark for adaptive routing."""

from adaptive_rag.models import Document
from adaptive_rag.pipeline import AdaptivePipeline
from adaptive_rag.retrieval.hybrid import SimpleReranker
from adaptive_rag.retrieval.memory import InMemoryRetriever

CASES = [
    ("What is retrieval augmented generation?", "adaptive_dense"),
    ("Compare dense retrieval versus hybrid retrieval and explain why", "adaptive_hybrid_graph"),
    ("What is the latest status today?", "adaptive_web_hybrid"),
]


def main() -> None:
    pipeline = AdaptivePipeline(
        InMemoryRetriever(
            [Document(id="d1", text="retrieval augmented generation uses external evidence")]
        ),
        SimpleReranker(),
    )
    passed = 0
    for query, expected in CASES:
        actual = pipeline.run(query).strategy
        ok = actual == expected
        passed += int(ok)
        print(f"{'PASS' if ok else 'FAIL'} | {query} | expected={expected} actual={actual}")
    accuracy = passed / len(CASES)
    print(f"routing_accuracy={accuracy:.2%}")
    if accuracy < 1.0:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
