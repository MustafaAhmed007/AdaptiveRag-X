from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader

from .config import settings
from .middleware import auth_and_rate_limit
from .models import QueryRequest, QueryResponse
from .pipeline import AdaptivePipeline
from .services import ingest_text

app = FastAPI(
    title="AdaptiveRAG-X",
    version="1.1.0",
    description="Adaptive, self-evaluating RAG with hybrid, graph, web and provider boundaries.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)
pipeline = AdaptivePipeline()
api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)


@app.middleware("http")
async def security_middleware(request, call_next):
    await auth_and_rate_limit(request)
    return await call_next(request)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": settings.app_name, "environment": settings.environment}


@app.get("/ready")
def ready() -> dict:
    return {"status": "ready", "retrieval": "configured", "generation": settings.llm_provider}


@app.post("/v1/documents")
def add_document(payload: dict, _api_key: str | None = Depends(api_key_header)) -> dict:
    text = str(payload.get("text", "")).strip()
    if not text:
        raise HTTPException(status_code=400, detail="text is required")
    tenant_id = str(payload.get("tenant_id", "default"))
    docs = ingest_text(text, str(payload.get("source", "api")), payload.get("metadata", {}), tenant_id)
    pipeline.add_documents(docs)
    return {"indexed": len(docs), "document_ids": [doc.id for doc in docs], "tenant_id": tenant_id}


@app.post("/v1/query", response_model=QueryResponse)
def query(req: QueryRequest, _api_key: str | None = Depends(api_key_header)) -> QueryResponse:
    try:
        return pipeline.run(req.query, req.top_k)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
