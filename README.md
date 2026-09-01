# AdaptiveRAG-X

**Production-oriented adaptive Retrieval-Augmented Generation (RAG) reference system.**

AdaptiveRAG-X demonstrates how a RAG system can choose retrieval depth and strategy from query characteristics, recover from weak evidence, and expose measurable quality signals instead of treating every question identically.

[![CI](https://github.com/MustafaAhmed007/AdaptiveRag-X/actions/workflows/ci.yml/badge.svg)](https://github.com/MustafaAhmed007/AdaptiveRag-X/actions/workflows/ci.yml)

## System

```text
Query
  ↓
Profile: intent / complexity / freshness / multi-hop / risk
  ↓
Adaptive Plan
  ↓
Dense ──┐
BM25 ───┼→ Hybrid Fusion → Rerank
Web ────┤                         ↓
Graph ──┘                    Evidence Grade
                                  ↓
                       weak → rewrite/decompose → retry
                                  ↓
                           grounded generation
                                  ↓
                       verification + citations
                                  ↓
                            evaluation + trace
```

## Implemented end-to-end

- typed query intelligence and explainable routing
- dense-like local retrieval baseline
- real BM25 lexical retrieval implementation
- weighted hybrid retrieval fusion
- pluggable reranking boundary
- multi-hop query decomposition
- bounded adaptive query-rewrite recovery
- evidence quality evaluation
- answer groundedness measurement
- citation objects
- prompt-injection gate
- structured execution traces
- FastAPI indexing/query/health API
- deterministic local runtime with no API key required
- hosted-LLM provider boundary
- Docker and GitHub Actions CI
- tests and interview-oriented architecture documentation

## Quick start

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
source .venv/bin/activate
pip install -e '.[dev]'
uvicorn adaptive_rag.api:app --reload
```

Open `http://localhost:8000/docs`.

Index data:

```bash
curl -X POST http://localhost:8000/v1/documents \
  -H 'Content-Type: application/json' \
  -d '{"text":"Adaptive retrieval selects retrieval strategies according to query characteristics.","source":"demo"}'
```

Query:

```bash
curl -X POST http://localhost:8000/v1/query \
  -H 'Content-Type: application/json' \
  -d '{"query":"What does adaptive retrieval do?"}'
```

Quality gates:

```bash
ruff check adaptive_rag tests
pytest -q
```

## Repository map

```text
adaptive_rag/
├── api.py              # FastAPI application
├── models.py           # domain contracts
├── planner.py          # query intelligence + routing
├── pipeline.py         # adaptive orchestration
├── query.py            # rewrite/decomposition/citations
├── evaluation.py       # retrieval + grounding metrics
├── observability.py    # trace model
├── security.py         # input safety gate
├── providers.py        # generator provider boundary
├── services.py         # ingestion/chunking
└── retrieval/
    ├── base.py         # retrieval contract
    ├── memory.py       # deterministic local retriever
    ├── sparse.py       # BM25
    ├── hybrid.py       # fusion
    └── rerank.py       # reranking
benchmarks/             # reproducible benchmark runner
docs/                   # architecture + ADRs + interview guide
tests/                  # automated tests
.github/workflows/      # CI
```

## Design principles

1. **Interfaces before providers.** Infrastructure is replaceable.
2. **Evidence before prose.** Retrieval returns typed evidence.
3. **Measure before optimizing.** Quality, latency and cost belong together.
4. **Fail explicitly.** Weak evidence triggers bounded recovery.
5. **Deterministic core.** Provider variability is isolated at the edges.

## Production hardening path

The core is runnable locally. Production adapters belong behind the existing boundaries for Qdrant/vector storage, hosted embeddings, cross-encoder reranking, web search, graph retrieval, OpenTelemetry/Prometheus, authentication and durable persistence. They should be marked complete only after implementation and tests exist.

## Evaluation

The benchmark runner and evaluator are designed to prevent invented performance claims. Add a golden dataset, run the experiment, record the output, and promote only changes that improve the measured target without violating latency/cost budgets.

## Interview laboratory

`docs/interview-guide/` connects the implementation to questions around chunking, embeddings, BM25, hybrid search, reranking, routing, agentic recovery, evaluation, observability, security, cost and system design.

## Responsible provenance

This repository is an independent implementation of broadly known RAG and agentic-RAG engineering patterns. It does not claim ownership of general field concepts. Any third-party code incorporated in future changes must retain its applicable license and notices.

## License

MIT
