# AdaptiveRAG-X

**AdaptiveRAG-X is a production-oriented adaptive Retrieval-Augmented Generation system that chooses how much retrieval and reasoning a query needs instead of forcing every request through one fixed RAG pipeline.**

It is designed as a modular system: start with deterministic local retrieval for zero-cost development, then plug in real embeddings, Qdrant, web search, cross-encoder reranking and an LLM provider without rewriting the core orchestration layer.

## Why Adaptive RAG?

Traditional RAG commonly follows one path: embed → retrieve → generate. That is simple, but it can waste latency and money on easy questions while under-serving current, comparative or multi-hop questions.

AdaptiveRAG-X profiles the query first, then selects a retrieval strategy and bounded retry budget. The response is evaluated for evidence quality and groundedness before it is returned.

## System Flow

```text
Query
  │
  ▼
Security Gate ──► block prompt injection patterns
  │
  ▼
Query Profiler
  ├── intent
  ├── complexity
  ├── freshness
  └── multi-hop requirement
  │
  ▼
Adaptive Planner
  │
  ├── simple ─────────► dense/local retrieval
  ├── complex ────────► hybrid dense + BM25
  ├── multi-hop ──────► hybrid + entity graph
  └── current ────────► web adapter + hybrid
  │
  ▼
Fusion → Rerank → Evidence Evaluation
  │                    │
  │              weak evidence?
  │                    └──► bounded query rewrite → retry
  ▼
Grounded Generation
  │
  ▼
Citations + Confidence + Trace + Cost Estimate
```

## Architecture

```text
adaptive_rag/
├── api.py                 FastAPI HTTP surface
├── config.py              environment-driven configuration
├── models.py              typed domain contracts
├── planner.py             adaptive routing and query profiling
├── pipeline.py            orchestration loop
├── query.py               rewriting, decomposition and citations
├── providers.py           mock + OpenAI-compatible generation boundary
├── embeddings.py          deterministic + OpenAI embedding boundary
├── services.py            chunking and ingestion
├── storage.py              SQLite durable document store
├── middleware.py           API-key auth + rate limiting
├── security.py             prompt-injection gate
├── telemetry.py            logging/timing helpers
├── observability.py        request traces and cost estimates
├── evaluation.py           retrieval/groundedness evaluation
└── retrieval/
    ├── memory.py           deterministic local retrieval
    ├── sparse.py           BM25
    ├── hybrid.py           weighted fusion
    ├── graph.py            lightweight entity graph / multi-hop retrieval
    ├── qdrant.py           optional Qdrant vector adapter
    ├── web.py              configurable web-search adapter
    └── rerank.py           deterministic reranker

reranking.py                optional sentence-transformers cross encoder
```

## LLM and AI Stack

| Layer | Default / Included | Production Option | Purpose |
|---|---|---|---|
| Generation | `MockGenerator` | OpenAI Responses API | grounded answer generation |
| Primary LLM | — | GPT-4.1-mini (configurable) | efficient production generation |
| Embeddings | deterministic hash | `text-embedding-3-small` | semantic vector representation |
| Sparse retrieval | BM25 | BM25 / search engine | exact terms and identifiers |
| Dense retrieval | deterministic local baseline | Qdrant + real embeddings | semantic recall |
| Reranking | score reranker | CrossEncoder / MS MARCO | precision after retrieval |
| Graph | local entity graph | graph DB adapter | multi-hop relationships |
| Web | JSON endpoint adapter | search provider | freshness/current information |
| Evaluation | deterministic metrics | LLM/eval provider extension | quality gate |

The repository deliberately keeps provider integrations behind interfaces. No API key is hard-coded and the local path remains runnable without paid services.

## Technology Stack

| Category | Technology |
|---|---|
| Language | Python 3.11+ |
| API | FastAPI + Uvicorn |
| Validation | Pydantic v2 |
| Retrieval | Dense-like + BM25 + Hybrid + Graph + Web |
| Vector DB | Qdrant adapter (optional) |
| Durable storage | SQLite |
| Reranking | deterministic scorer; optional Sentence Transformers |
| Testing | Pytest |
| Linting | Ruff |
| CI | GitHub Actions |
| Packaging | `pyproject.toml` / setuptools |
| Containers | Docker + Compose |
| Configuration | environment variables / `.env` |
| Observability | request traces, timings, estimated cost, structured logging helpers |

## Quick Start

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell
# .venv\\Scripts\\Activate.ps1

pip install -e ".[dev]"
uvicorn adaptive_rag.api:app --reload
```

Open the API at `http://127.0.0.1:8000` and interactive OpenAPI documentation at `/docs`.

### Add knowledge

```bash
curl -X POST http://127.0.0.1:8000/v1/documents \
  -H "Content-Type: application/json" \
  -d '{"text":"AdaptiveRAG-X selects retrieval strategies based on query characteristics."}'
```

### Query

```bash
curl -X POST http://127.0.0.1:8000/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query":"What does AdaptiveRAG-X do?","top_k":5}'
```

## Production Configuration

Copy `.env.example` to `.env` and configure only the services you actually use. Important settings include:

- `LLM_PROVIDER` and `LLM_MODEL`
- `OPENAI_API_KEY`
- `EMBEDDING_PROVIDER`
- `QDRANT_URL` and `QDRANT_COLLECTION`
- `DATABASE_URL`
- `WEB_SEARCH_URL`
- `ADAPTIVE_RAG_API_KEY`
- `MAX_REQUESTS_PER_MINUTE`

For production, enable an API key, put the service behind TLS/reverse proxy infrastructure, use a managed database/vector store, and restrict CORS to known origins.

## Quality Gates

```bash
ruff check adaptive_rag tests benchmarks
pytest -q
python -m benchmarks.run
```

GitHub Actions runs these checks automatically on pushes and pull requests.

## Evaluation Philosophy

AdaptiveRAG-X does not claim that a retrieval score proves an answer is correct. The evaluation layer separately tracks retrieval relevance, context precision, context recall, groundedness and citation coverage, then produces a conservative aggregate signal. This makes quality visible and gives the planner a measurable basis for bounded retries.

## Design Principles

1. **Adaptive, not one-size-fits-all.**
2. **Evidence before generation.**
3. **Bounded retries, never uncontrolled agent loops.**
4. **Provider-agnostic boundaries.**
5. **Local-first development with production adapters.**
6. **Tenant metadata is carried through the domain model.**
7. **Security is part of the pipeline, not an afterthought.**
8. **Measure quality, latency and cost together.**
9. **Never fake an integration: optional services are explicit.**

## Repository Status

The repository contains a runnable adaptive-RAG core plus production-oriented integration boundaries for embeddings, Qdrant, web retrieval, cross-encoder reranking, durable storage, API security, rate limiting and observability. Optional external services remain opt-in because they require credentials or infrastructure that cannot be safely bundled into source control.

## License

MIT
