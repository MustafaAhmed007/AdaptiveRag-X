"""Deterministic smoke benchmark; reports measured routing accuracy only."""
from adaptive_rag.models import Document
from adaptive_rag.pipeline import AdaptivePipeline
from adaptive_rag.retrieval.hybrid import SimpleReranker
from adaptive_rag.retrieval.memory import InMemoryRetriever
CASES=[('What is retrieval augmented generation?','adaptive_dense'),('Compare dense retrieval versus hybrid retrieval','adaptive_hybrid_graph'),('What is the latest status today?','adaptive_web_hybrid')]
def main():
    pipeline=AdaptivePipeline(InMemoryRetriever([Document(id='d1',text='retrieval augmented generation uses external evidence')]),SimpleReranker()); passed=0
    for query,expected in CASES:
        actual=pipeline.run(query).strategy; ok=actual==expected; passed+=ok; print(f"{'PASS' if ok else 'FAIL'} | {query} | expected={expected} actual={actual}")
    print(f'routing_accuracy={passed/len(CASES):.2%}')
if __name__=='__main__': main()
