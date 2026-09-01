from fastapi import FastAPI, HTTPException
from .models import Document, QueryRequest, QueryResponse
from .pipeline import AdaptivePipeline
from .retrieval.memory import InMemoryRetriever
from .retrieval.hybrid import SimpleReranker

app = FastAPI(title="AdaptiveRAG-X", version="0.1.0")
retriever = InMemoryRetriever([
    Document(id="rag-1", source="knowledge/rag.txt", text="Retrieval-augmented generation combines retrieval with generation so a model can answer using external evidence."),
    Document(id="rag-2", source="knowledge/adaptive.txt", text="Adaptive RAG selects retrieval behavior based on query intent, complexity, freshness and evidence quality."),
    Document(id="rag-3", source="knowledge/evaluation.txt", text="RAG evaluation should measure retrieval quality, grounding, citation coverage, latency and cost."),
])
pipeline = AdaptivePipeline(retriever, SimpleReranker())

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "adaptive-rag-x"}

@app.post("/v1/query", response_model=QueryResponse)
def query(request: QueryRequest) -> QueryResponse:
    try:
        return pipeline.run(request.query, request.top_k)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

@app.post("/v1/documents")
def add_document(document: Document) -> dict[str, str]:
    retriever.add(document)
    return {"status": "indexed", "document_id": document.id}
