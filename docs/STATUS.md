# Implementation Status

AdaptiveRAG-X is a runnable adaptive-RAG core with local-first defaults and opt-in production adapters.

## Implemented

- query profiling and adaptive routing
- dense-like local retrieval
- BM25 sparse retrieval
- weighted hybrid fusion
- multi-hop query decomposition
- lightweight entity graph retrieval
- configurable web retrieval adapter
- deterministic and optional cross-encoder reranking
- evidence evaluation and groundedness checks
- bounded rewrite/retry loop
- citations and request traces
- configurable OpenAI generation boundary
- deterministic and OpenAI embedding boundaries
- SQLite document persistence
- tenant metadata propagation
- API-key authentication and rate limiting
- Docker packaging and health checks
- tests, benchmark and GitHub Actions CI

## External infrastructure

Qdrant, OpenAI and a web-search service are intentionally optional. They become active through environment configuration and credentials; they are not falsely represented as embedded services.
