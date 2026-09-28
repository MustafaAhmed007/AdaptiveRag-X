# AdaptiveRAG-X

**AdaptiveRAG-X is an adaptive Retrieval-Augmented Generation (RAG) platform that dynamically chooses retrieval depth, search strategy, reranking and bounded reasoning based on the query.**

Instead of forcing every question through the same `embed → retrieve → generate` path, AdaptiveRAG-X first asks what the query actually needs. Simple factual questions can take a fast local path. Comparative and exploratory questions can use hybrid retrieval. Multi-hop questions can activate graph-assisted retrieval. Freshness-sensitive questions can use web retrieval. Weak evidence triggers a bounded rewrite-and-retry loop before generation.

The project is designed to be **local-first, provider-agnostic, testable and production-oriented**. The core can run without paid model APIs, while real embeddings, Qdrant, web search, cross-encoder reranking and LLM providers remain explicit configuration options.

> Build once. Route intelligently. Measure continuously. Improve from evidence.

---

## Why Adaptive RAG?

Traditional RAG is powerful, but a fixed pipeline creates predictable trade-offs:

- Easy questions can receive unnecessary retrieval and reasoning.
- Exact identifiers and terminology may benefit from sparse search.
- Semantic questions benefit from dense retrieval.
- Difficult comparisons often need hybrid retrieval plus reranking.
- Multi-hop questions may require relationship-aware retrieval.
- Current questions need fresh external evidence.
- Low-quality retrieval should be detected before generation rather than hidden behind fluent prose.

AdaptiveRAG-X turns these choices into an explicit orchestration layer. The planner profiles each query, selects a strategy, evaluates the evidence and retries only within a bounded budget.

## System Flow

```text
                         ┌──────────────────────┐
                         │      USER QUERY      │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │    SECURITY GATE     │
                         │ injection / safety    │
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
                                    │   bounded retry
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
| Short factual | Fast dense/local | Lowest practical latency |
| Explanatory | Hybrid | Semantic + lexical coverage |
| Comparison | Hybrid + reranking | Candidate breadth + precision |
| Multi-hop | Hybrid + graph | Relationship-aware evidence |
| Current/fresh | Web + hybrid | Fresh external evidence |
| Weak retrieval | Rewrite + bounded retry | Recover evidence quality |

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
├── research.py            multi-aspect research workflow
└── retrieval/
    ├── base.py            retriever contract
    ├── memory.py          deterministic local retrieval
    ├── sparse.py          BM25 retrieval
    ├── hybrid.py          dense/sparse fusion
    ├── graph.py           tenant-aware graph retrieval
    ├── qdrant.py          tenant-aware Qdrant adapter
    ├── web.py             configurable web-search adapter
    └── rerank.py          deterministic reranking

benchmarks/                deterministic routing benchmarks
docs/                      project documentation
tests/                     regression and integration tests
.github/workflows/         CI quality gates
```

## LLM & AI Stack

| Layer | Included baseline | Production / configurable option | Role |
|---|---|---|---|
| Generation | `MockGenerator` | OpenAI Responses API | Grounded response synthesis |
| Embeddings | `HashEmbedder` | OpenAI `text-embedding-3-small` or compatible provider | Semantic vectors |
| Sparse retrieval | BM25 | BM25/search-engine adapter | Exact terms, IDs, keywords |
| Dense retrieval | Deterministic local baseline | Qdrant + real embeddings | Semantic recall |
| Hybrid retrieval | Weighted fusion | Production fusion strategy | Combined recall |
| Reranking | Score reranker | Sentence Transformers / cross-encoder | Precision refinement |
| Graph retrieval | Lightweight entity graph | Graph database adapter | Multi-hop relationships |
| Web retrieval | JSON endpoint adapter | Search provider | Current information |
| Evaluation | Deterministic metrics | External/LLM evaluator extension | Quality gates |

**No model API key is committed to the repository.** Provider integrations are explicit so the same orchestration can move between local development and production infrastructure.

## Technology Stack

| Category | Technology | Why it is here |
|---|---|---|
| Language | Python 3.11+ | Mature AI/data ecosystem |
| API | FastAPI + Uvicorn | Typed, fast HTTP interface |
| Validation | Pydantic v2 | Reliable domain contracts |
| Retrieval | Dense-like + BM25 + Hybrid + Graph + Web | Adaptive evidence acquisition |
| Vector database | Qdrant adapter | Scalable semantic retrieval |
| Durable storage | SQLite baseline | Zero-dependency local persistence |
| Reranking | Deterministic + optional CrossEncoder | Improve evidence precision |
| Testing | Pytest | Regression protection |
| Linting | Ruff | Fast static quality gate |
| CI | GitHub Actions | Automated verification |
| Packaging | `pyproject.toml` | Reproducible Python package |
| Containers | Docker + Compose | Portable deployment |
| Configuration | Environment variables / `.env` | Secret-safe local configuration |
| Observability | Traces + timings + cost signals | Operational feedback |

## Quick Start

### 1. Create a virtual environment

```bash
python -m venv .venv
```

### 2. Activate it

**Linux/macOS**

```bash
source .venv/bin/activate
```

**Windows PowerShell**

```powershell
.\.venv\Scripts\Activate.ps1
```

**Windows CMD**

```cmd
.venv\Scripts\activate
```

### 3. Install the project

```bash
python -m pip install -e ".[dev]"
```

### 4. Configure local environment

Copy `.env.example` to `.env` and set the values you need.

At minimum, protected API endpoints require:

```text
ADAPTIVE_RAG_API_KEY=replace-with-a-local-secret
```

Keep the real `.env` out of source control. Only `.env.example` belongs in the repository.

### 5. Run the API

```bash
uvicorn adaptive_rag.api:app --reload
```

The API exposes:

- `GET /health` — public health check.
- `GET /ready` — authenticated readiness check.
- `POST /v1/documents` — authenticated document ingestion.
- `POST /v1/query` — authenticated adaptive RAG query.
- `POST /v1/research` — authenticated multi-aspect research.

Interactive API documentation is available at:

```text
http://127.0.0.1:8000/docs
```

## API Authentication

Protected endpoints require the `x-api-key` HTTP header.

Example:

```bash
curl http://127.0.0.1:8000/ready \
  -H "x-api-key: YOUR_API_KEY"
```

Document ingestion:

```bash
curl -X POST http://127.0.0.1:8000/v1/documents \
  -H "Content-Type: application/json" \
  -H "x-api-key: YOUR_API_KEY" \
  -d '{"text":"AdaptiveRAG-X selects retrieval strategies based on query characteristics.","tenant_id":"default"}'
```

Query:

```bash
curl -X POST http://127.0.0.1:8000/v1/query \
  -H "Content-Type: application/json" \
  -H "x-api-key: YOUR_API_KEY" \
  -d '{"query":"What does AdaptiveRAG-X do?","top_k":5,"tenant_id":"default"}'
```

The `/health` endpoint remains public so basic process health can be checked without credentials. Other API routes are protected by the authentication middleware.

## Tenant Isolation

Documents and retrieval operations carry a `tenant_id`. Supported retrieval paths apply tenant filtering so evidence from one tenant is not returned to another tenant during retrieval.

This includes:

- in-memory retrieval
- BM25 retrieval
- hybrid retrieval
- graph retrieval
- Qdrant retrieval

Qdrant documents also persist the tenant identifier in their payload, and Qdrant queries apply a tenant filter.

### Important authorization boundary

The current API accepts `tenant_id` from the request. Tenant filtering therefore provides **data partitioning**, but a single shared API key does not by itself establish identity-bound authorization between tenants.

For a true multi-tenant deployment, bind the tenant identity to an authenticated principal, token, session or gateway-issued identity instead of trusting a caller-supplied tenant identifier.

## Security

AdaptiveRAG-X currently includes several security-oriented controls:

- API-key authentication for protected endpoints.
- Fail-closed behavior when API authentication is not configured.
- In-memory request rate limiting.
- Prompt-injection detection at the pipeline security gate.
- Tenant-filtered retrieval across supported retrievers.
- SSRF protection for remote research URLs, including blocking common local/private/link-local/reserved destinations and validating resolved addresses.
- Environment-based configuration for credentials rather than hardcoded API keys.

### Research URL safety

Remote research URLs are validated before retrieval to reduce SSRF risk. The current protection checks the supplied URL and its resolved addresses.

The application should still be deployed behind normal network controls and should not be treated as a substitute for an egress firewall or hardened HTTP client.

### Local research files

The research API also accepts local file paths. This is intended for trusted/local use. **Do not expose arbitrary local-file research access to untrusted callers without adding an explicit filesystem allowlist or sandbox.**

## Production Configuration

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

For production, additionally use:

- TLS/HTTPS.
- A managed database and vector store where appropriate.
- Restricted CORS origins instead of a permissive development configuration.
- A proper secret manager.
- Network egress controls.
- Authenticated tenant identity rather than caller-supplied tenant IDs.
- Monitoring and centralized logging.
- A hardened filesystem policy for research inputs.
- An authenticated API gateway where appropriate.

Never commit API keys or other credentials to the repository. GitHub recommends keeping credentials out of source control and using environment variables, encrypted secrets or a secret manager instead. citeturn0search0turn0search1

## Quality & Evaluation

Run the test suite:

```bash
pytest -q
```

Run linting:

```bash
ruff check adaptive_rag tests benchmarks
```

Run benchmarks:

```bash
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

### Current verified baseline

The current development checkout has a passing automated test suite:

```text
15 passed
```

The exact count can change as additional regression and security tests are added.

## Repository Structure

```text
AdaptiveRag-X/
├── .github/              CI workflows
├── adaptive_rag/         application package
├── benchmarks/           benchmark suite
├── docs/                 documentation
├── tests/                automated tests
├── .env.example          configuration template
├── Dockerfile            container image
├── docker-compose.yml     local container orchestration
├── install.ps1            Windows installer
├── install.sh             Unix installer
├── Makefile               development commands
├── pyproject.toml         package/dependency configuration
├── README.md              project documentation
├── SECURITY.md            security policy
├── CONTRIBUTING.md        contribution guide
├── CHANGELOG.md           change history
└── LICENSE                MIT license
```

Local/generated directories such as `.venv/`, `.pytest_cache/`, `.ruff_cache/` and `*.egg-info/` are development artifacts and are not part of the source distribution.

## Design Principles

1. **Adaptive, not one-size-fits-all.**
2. **Evidence before generation.**
3. **Bounded retries, never uncontrolled agent loops.**
4. **Provider-agnostic boundaries.**
5. **Local-first development with production adapters.**
6. **Tenant-aware domain contracts and retrieval filters.**
7. **Security belongs inside the pipeline.**
8. **Measure quality, latency and cost together.**
9. **Make integrations explicit rather than faking capabilities.**
10. **Prefer reproducible benchmarks over marketing claims.**

## Project Status

AdaptiveRAG-X contains a runnable adaptive-RAG core plus production-oriented boundaries for embeddings, Qdrant, web retrieval, graph retrieval, reranking, durable storage, authentication, rate limiting, evaluation and observability.

The repository is intentionally explicit about the difference between:

- **local deterministic functionality** that works without external credentials,
- **optional provider integrations** that require external services,
- and **production hardening** that must be supplied by the deployment environment.

The project should be treated as an actively developed engineering system rather than a claim of universal RAG correctness or complete production security.

## License

MIT
