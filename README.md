# AdaptiveRAG-X

**AdaptiveRAG-X is an adaptive Retrieval-Augmented Generation (RAG) platform that dynamically chooses retrieval depth, search strategy, reranking and bounded reasoning based on the query.**

Instead of forcing every question through the same `embed → retrieve → generate` path, AdaptiveRAG-X asks a more useful question first: **what does this query actually need?** Simple factual questions can take a fast path. Comparative and exploratory questions can use broader hybrid retrieval. Multi-hop questions can activate graph-assisted retrieval. Freshness-sensitive questions can use the web adapter. Weak evidence triggers a bounded rewrite-and-retry loop before generation.

The project is designed to be **local-first, provider-agnostic, testable and production-oriented**. You can run the core without paid APIs, then connect real embeddings, Qdrant, web search, cross-encoder reranking and an LLM through explicit configuration and provider boundaries.

> Build once. Route intelligently. Measure continuously. Improve from evidence.

## Why Adaptive RAG?

Traditional RAG is powerful, but a fixed pipeline creates predictable trade-offs:

- Easy questions can receive unnecessary retrieval and reasoning.
- Exact identifiers and terminology may benefit from sparse search.
- Semantic questions benefit from dense retrieval.
- Difficult comparisons often need hybrid retrieval plus reranking.
- Multi-hop questions may require relationship-aware retrieval.
- Current questions need fresh external evidence.
- Low-quality retrieval should be detected before generation rather than hidden behind fluent prose.

AdaptiveRAG-X turns those choices into an explicit orchestration layer. The planner profiles each query, selects a strategy, evaluates the evidence and retries only within a bounded budget.

## System Flow

```text
                         ┌──────────────────────┐
                         │        USER QUERY    │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │    SECURITY GATE     │
                         │ injection / policy   │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │    QUERY PROFILER    │
                         │ intent / complexity  │
                         │ freshness / multi-hop│
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │   ADAPTIVE PLANNER   │
                         └──────────┬───────────┘
                                    │
             ┌────────────────────┼────────────────────┐
             ▼                    ▼                    ▼
       Fast / Dense         Hybrid + BM25        Graph / Web
             │                    │                    │
             └────────────────────┼────────────────────┘
                                  ▼
                         ┌──────────────────────┐
                         │ FUSION + RERANKING   │
                         └──────────┬───────────┘
                                    ▼
                         ┌──────────────────────┐
                         │  EVIDENCE EVALUATOR  │
                         └──────────┬───────────┘
                                    │
                         weak? ─────┴───── yes
                                    │          │
                                   no          ▼
                                    │   QUERY REWRITE
                                    │          │
                                    │    bounded retry
                                    │          │
                                    └──────────┘
                                    ▼
                         ┌──────────────────────┐
                         │  GROUNDED GENERATION │
                         └──────────┬───────────┘
                                    ▼
                    ┌─────────────────────────────────┐
                    │ answer + citations + confidence │
                    │ trace + attempts + cost signal  │
                    └─────────────────────────────────┘
```

## Adaptive Strategy Matrix

| Query type | Strategy | Objective |
|---|---|---|
| Short factual | Fast dense/local | lowest practical latency |
| Explanatory | Hybrid | semantic + lexical coverage |
| Comparison | Hybrid + reranking | candidate breadth + precision |
| Multi-hop | Hybrid + graph | relationship-aware evidence |
| Current/fresh | Web + hybrid | fresh external evidence |
| Weak retrieval | Rewrite + bounded retry | recover evidence quality |

## Architecture

```text
adaptive_rag/
├── api.py                 FastAPI HTTP API
├── config.py              environment-driven configuration
├── models.py              typed domain contracts
├── planner.py             query profiling + adaptive planning
├── pipeline.py            end-to-end orchestration
├── query.py               rewrite + decomposition + citations
├── providers.py           generation provider boundary
├── embeddings.py          embedding provider boundary
├── services.py            ingestion + chunking
├── storage.py             durable document storage
├── middleware.py          API-key auth + rate limiting
├── security.py            prompt-injection gate
├── telemetry.py           logging/timing helpers
├── observability.py       traces + cost estimates
├── evaluation.py          retrieval + grounding metrics
└── retrieval/
    ├── memory.py          deterministic local retrieval
    ├── sparse.py          BM25 retrieval
    ├── hybrid.py          dense/sparse fusion
    ├── graph.py           entity graph retrieval
    ├── qdrant.py          Qdrant vector adapter
    ├── web.py             configurable web-search adapter
    └── rerank.py          deterministic reranking

reranking.py               optional cross-encoder reranker
benchmarks/                deterministic routing benchmark
examples/                  runnable examples / seed knowledge
scripts/                   developer and release helpers
.github/workflows/         CI quality gates
```

## LLM & AI Stack

| Layer | Included baseline | Production / configurable option | Role |
|---|---|---|---|
| Generation | `MockGenerator` | OpenAI Responses API | grounded response synthesis |
| Primary LLM | local/no-key mode | GPT-4.1-mini or another compatible model | answer generation |
| Embeddings | deterministic local embedder | OpenAI `text-embedding-3-small` or compatible provider | semantic vectors |
| Sparse retrieval | BM25 | BM25/search-engine adapter | exact terms, IDs, keywords |
| Dense retrieval | deterministic dense-like baseline | Qdrant + real embeddings | semantic recall |
| Hybrid retrieval | weighted fusion | production fusion strategy | combined recall |
| Reranking | score reranker | Sentence Transformers / cross-encoder | precision refinement |
| Graph retrieval | lightweight entity graph | graph database adapter | multi-hop relationships |
| Web retrieval | JSON endpoint adapter | search provider | current information |
| Evaluation | deterministic metrics | external/LLM evaluator extension | quality gates |

**No model API key is committed to the repository.** Provider integrations are explicit so the same orchestration can move between local development and production infrastructure.

## Technology Stack

| Category | Technology | Why it is here |
|---|---|---|
| Language | Python 3.11+ | mature AI/data ecosystem |
| API | FastAPI + Uvicorn | typed, fast HTTP interface |
| Validation | Pydantic v2 | reliable domain contracts |
| Retrieval | Dense-like + BM25 + Hybrid + Graph + Web | adaptive evidence acquisition |
| Vector database | Qdrant adapter | scalable semantic retrieval |
| Durable storage | SQLite baseline | zero-dependency local persistence |
| Reranking | deterministic + optional CrossEncoder | improve evidence precision |
| Testing | Pytest | regression protection |
| Linting | Ruff | fast static quality gate |
| CI | GitHub Actions | automated verification |
| Packaging | `pyproject.toml` | reproducible Python package |
| Containers | Docker + Compose | portable deployment |
| Configuration | environment variables | secret-safe deployment |
| Observability | traces + timings + cost signals | operational feedback |

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

Open `http://127.0.0.1:8000/docs` for interactive API documentation.

### Add knowledge

```bash
curl -X POST http://127.0.0.1:8000/v1/documents \
  -H "Content-Type: application/json" \
  -d '{"text":"AdaptiveRAG-X selects retrieval strategies based on query characteristics."}'
```

### Query the system

```bash
curl -X POST http://127.0.0.1:8000/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query":"What does AdaptiveRAG-X do?","top_k":5}'
```

## Production Configuration

Copy `.env.example` to `.env` and configure only the infrastructure you actually use.

Important settings include:

- `LLM_PROVIDER`
- `LLM_MODEL`
- `OPENAI_API_KEY`
- `EMBEDDING_PROVIDER`
- `QDRANT_URL`
- `QDRANT_COLLECTION`
- `DATABASE_URL`
- `WEB_SEARCH_URL`
- `ADAPTIVE_RAG_API_KEY`
- `MAX_REQUESTS_PER_MINUTE`

For production, use TLS, a managed database/vector store, restricted CORS, secret management, monitoring and an authenticated API gateway.

## Quality & Evaluation

```bash
ruff check adaptive_rag tests benchmarks
pytest -q
python -m benchmarks.run
```

The evaluation layer separates several signals rather than pretending that one score proves correctness:

- retrieval relevance
- context precision
- context recall
- groundedness
- citation coverage
- aggregate evidence quality

This creates a feedback loop for adaptive routing and bounded recovery.

## Growth & Virality Strategy

AdaptiveRAG-X is structured not only as a codebase, but as a **discoverable open-source project**. The goal is to make every useful concept easy to understand, demonstrate, search for and share.

### 1. Search-driven technical content

The repository naturally maps to high-intent topics such as:

- adaptive RAG
- agentic RAG
- hybrid RAG
- RAG evaluation
- BM25 vs dense retrieval
- reranking for RAG
- multi-hop RAG
- GraphRAG architecture
- production RAG pipelines
- cost-aware LLM systems
- grounded generation
- retrieval routing

Architecture and evaluation documentation can become standalone technical articles, examples and benchmark discussions without changing the core engine.

### 2. Shareable demonstrations

The most viral asset is not a claim that the system is "better". It is a reproducible demonstration.

Recommended public demo loop:

```text
Question
   ↓
Router decision
   ↓
Selected retrieval strategy
   ↓
Evidence returned
   ↓
Reranking
   ↓
Quality score
   ↓
Final answer + citations
```

This makes the invisible RAG decision process visible and gives developers something concrete to compare, fork and discuss.

### 3. Benchmark-led growth

Every meaningful retrieval improvement should be measurable. The project includes deterministic benchmark infrastructure so future experiments can publish:

- routing accuracy
- retrieval quality
- latency
- retry rate
- citation coverage
- estimated cost

That creates a compounding engineering loop: **experiment → measure → document → share → attract contributors → improve → repeat**.

### 4. SEO-friendly documentation architecture

Documentation should target questions developers actually search for rather than keyword stuffing. The project structure supports dedicated guides for adaptive routing, hybrid retrieval, reranking, GraphRAG, evaluation, deployment and provider integration.

Each guide should link back to runnable examples and benchmarks, creating a strong internal knowledge graph instead of isolated pages.

### 5. Open-source contribution flywheel

```text
Useful repository
      ↓
Clear README + architecture
      ↓
Runnable examples
      ↓
Benchmarks + transparent results
      ↓
Issues / discussions / contributions
      ↓
New integrations and experiments
      ↓
More documentation + demos
      ↓
More discovery and adoption
      └───────────────↺
```

This is the intended growth engine. **Virality cannot be guaranteed**, so the system is optimized for shareability, reproducibility, search intent, technical credibility and low-friction contribution instead of artificial growth claims.

## Recommended Content Surface

For a serious public launch, the strongest companion pages are:

1. **Adaptive RAG explained** — why routing beats one fixed pipeline.
2. **Hybrid RAG guide** — BM25 + dense retrieval + reranking.
3. **RAG evaluation guide** — how to measure groundedness and citation coverage.
4. **Adaptive RAG benchmark** — reproducible routing/quality/latency results.
5. **Production deployment guide** — Qdrant, LLM provider and observability setup.
6. **Architecture deep dive** — planner, retrievers, evaluator and recovery loop.
7. **Examples cookbook** — practical RAG patterns developers can copy.

These topics form a connected technical content cluster rather than disconnected SEO pages.

## Design Principles

1. **Adaptive, not one-size-fits-all.**
2. **Evidence before generation.**
3. **Bounded retries, never uncontrolled agent loops.**
4. **Provider-agnostic boundaries.**
5. **Local-first development with production adapters.**
6. **Tenant-aware domain contracts.**
7. **Security belongs inside the pipeline.**
8. **Measure quality, latency and cost together.**
9. **Make integrations explicit rather than faking capabilities.**
10. **Prefer reproducible benchmarks over marketing claims.**

## Repository Status

AdaptiveRAG-X contains a runnable adaptive-RAG core plus production-oriented boundaries for embeddings, Qdrant, web retrieval, graph retrieval, reranking, durable storage, authentication, rate limiting and observability. External services remain opt-in because they require credentials or infrastructure outside source control.

The repository is intentionally honest about what runs locally versus what requires external infrastructure.

## License

MIT
