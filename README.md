# AdaptiveRAG-X

> **Self-evaluating, cost-aware, hybrid and agentic Retrieval-Augmented Generation platform.**

[![CI](https://github.com/MustafaAhmed007/AdaptiveRag-X/actions/workflows/ci.yml/badge.svg)](https://github.com/MustafaAhmed007/AdaptiveRag-X/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-black.svg)](LICENSE)

AdaptiveRAG-X is a production-oriented RAG reference implementation designed around one principle: **retrieval should adapt to the question instead of forcing every question through the same pipeline.**

It combines query intelligence, strategy selection, dense/sparse/hybrid retrieval abstractions, reranking, evidence grading, iterative recovery, answer verification, citations, cost/latency telemetry, security gates, and reproducible evaluation.

## Architecture

```text
                         ┌─────────────────────┐
                         │       Query         │
                         └──────────┬──────────┘
                                    │
                         ┌──────────▼──────────┐
                         │   Query Intelligence │
                         │ intent/complexity/  │
                         │ freshness/risk      │
                         └──────────┬──────────┘
                                    │
                         ┌──────────▼──────────┐
                         │  Adaptive Planner   │
                         └──────────┬──────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              │                     │                     │
        Dense retrieval       Sparse retrieval       Web / Graph
              │                     │                     │
              └─────────────────────┼─────────────────────┘
                                    │
                         ┌──────────▼──────────┐
                         │ Hybrid + Reranking  │
                         └──────────┬──────────┘
                                    │
                         ┌──────────▼──────────┐
                         │ Evidence Grader     │
                         └──────────┬──────────┘
                                    │
                         insufficient evidence?
                              │             │
                             yes            no
                              │             │
                    rewrite/decompose      ▼
                              │      ┌───────────────┐
                              └─────►│ Grounded LLM  │
                                     └───────┬───────┘
                                             │
                                     ┌───────▼───────┐
                                     │ Verify + Cite │
                                     └───────┬───────┘
                                             │
                                     ┌───────▼───────┐
                                     │ Eval + Trace  │
                                     └───────────────┘
```

## What makes it different

- **Adaptive routing:** strategy is selected from query characteristics.
- **Hybrid retrieval:** dense and lexical retrieval can be fused.
- **Reranking boundary:** retrieval and precision ranking are separate concerns.
- **Evidence-first generation:** answers are built from explicit evidence objects.
- **Recovery loop:** weak evidence triggers rewrite/decomposition rather than blind generation.
- **Verification:** generated answers can be checked for grounding and citation coverage.
- **Cost awareness:** every run records model/tool usage and estimated cost.
- **Observability:** a trace captures decisions, latency and retrieval behavior.
- **Security:** prompt-injection and unsafe-tool checks are first-class pipeline stages.
- **Evaluation:** benchmark adapters and deterministic unit tests live beside the system.

## Quick start

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
uvicorn adaptive_rag.api:app --reload
```

Open `http://localhost:8000/docs`.

### Example request

```bash
curl -X POST http://localhost:8000/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query":"What is retrieval augmented generation?"}'
```

The default local runtime uses deterministic in-memory retrieval and a mock generator, so the architecture and tests work **without an API key**. Provider adapters can be added behind the interfaces in `adaptive_rag/providers/`.

## Project map

```text
adaptive_rag/
├── api.py                 # FastAPI application
├── config.py              # typed settings
├── models.py              # domain contracts
├── planner.py             # adaptive strategy selection
├── pipeline.py            # orchestration and recovery loop
├── security.py            # input/tool safety gates
├── evaluation.py          # evaluation primitives
├── observability.py       # traces and usage accounting
├── retrieval/             # dense/sparse/hybrid/rerank interfaces
├── providers/             # model/search provider boundaries
└── services/              # ingestion and application services
benchmarks/                # golden datasets and benchmark runner
experiments/               # reproducible experiment definitions
docs/                     # architecture, ADRs and interview guide
tests/                    # unit/integration tests
.github/workflows/         # CI
```

## Engineering principles

1. **Interfaces before integrations.** Providers are replaceable.
2. **Evidence before prose.** Retrieval outputs are structured objects.
3. **Measure before optimizing.** Quality, latency and cost are tracked together.
4. **Fail explicitly.** Weak evidence is a recoverable state, not a hidden failure.
5. **Keep the core deterministic.** External model behavior is isolated at the edges.

## Evaluation

Run the local benchmark:

```bash
python -m benchmarks.run
pytest -q
```

The benchmark compares routing decisions and evidence quality. Provider-backed evaluation can be enabled later without changing the core contracts.

## Interview laboratory

See [`docs/interview-guide/`](docs/interview-guide/) for concise explanations and questions covering chunking, hybrid search, reranking, routing, agentic RAG, evaluation, observability, security and cost optimization.

## Responsible provenance

This repository is an independent implementation and extension of general RAG/agentic-RAG engineering patterns. It does not claim ownership of the underlying field concepts. Where third-party code is reused, its license and notices must be preserved.

## Roadmap

- [x] Typed query intelligence and adaptive planner
- [x] Evidence contracts and recovery loop
- [x] Dense/sparse/hybrid retrieval interfaces
- [x] Reranking abstraction
- [x] Evaluation and telemetry primitives
- [x] Security gate
- [x] FastAPI API
- [x] CI and tests
- [ ] Production Qdrant adapter
- [ ] BM25 implementation adapter
- [ ] Cross-encoder reranker adapter
- [ ] Graph retrieval adapter
- [ ] Web-search adapter
- [ ] OpenTelemetry/Prometheus exporters
- [ ] Full benchmark suite with provider-backed models

## License

MIT — see [LICENSE](LICENSE).
