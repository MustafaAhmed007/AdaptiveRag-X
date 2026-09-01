# AdaptiveRAG-X Architecture

## Core idea

AdaptiveRAG-X treats retrieval as a policy decision rather than a fixed chain. The planner profiles each query, selects an appropriate retrieval budget, and uses evaluation to decide whether a bounded recovery attempt is justified.

## Runtime flow

```text
request → security → profile → plan → retrieve → fuse → rerank
                                      ↓                 ↓
                                graph / web        evaluate evidence
                                      ↓                 ↓
                                  rewrite ← weak ← quality gate
                                      ↓
                              grounded generation
                                      ↓
                           citations / confidence / trace
```

## Routing policy

| Profile | Strategy | Primary reason |
|---|---|---|
| Short factual | dense/local | low latency and cost |
| Explanatory | hybrid | semantic + lexical coverage |
| Comparison | hybrid + rerank | candidate breadth + precision |
| Multi-hop | hybrid + graph | relationship traversal |
| Freshness-sensitive | web + hybrid | current external evidence |

## Retrieval stack

- **Dense boundary:** `Embedder` supports deterministic local vectors and OpenAI embeddings.
- **Sparse:** BM25 captures exact terminology, identifiers and lexical matches.
- **Hybrid:** weighted fusion combines dense-like and sparse candidates.
- **Graph:** an entity-overlap graph provides a dependency-free multi-hop baseline.
- **Vector DB:** `QdrantRetriever` is an optional production adapter.
- **Web:** `WebRetriever` accepts a compatible JSON search endpoint.
- **Reranking:** deterministic scorer is always available; a CrossEncoder adapter is optional.

## Generation stack

The pipeline uses a provider boundary. `MockGenerator` makes the repository executable without credentials. `ProviderGenerator` uses an injected OpenAI-compatible client and a grounded system instruction. The model is configured through environment variables rather than source code.

## Persistence and tenancy

`SQLiteDocumentStore` provides a durable local document store with tenant IDs and versions. The domain model carries tenant metadata into ingestion and vector payloads. A production deployment should add database-level isolation and authorization policies appropriate to its threat model.

## Safety and reliability

1. Prompt-injection patterns are rejected before retrieval.
2. API-key authentication is optional for local development and can be required in production.
3. Per-client rate limiting prevents accidental runaway traffic.
4. Retrieval retries are bounded by query complexity.
5. Evaluation exposes retrieval relevance, context precision/recall, groundedness and citation coverage.
6. Trace IDs, attempt counts and estimated costs make each response diagnosable.

## Operational model

The local configuration has no mandatory external services. Production deployments can progressively add a real embedding provider, Qdrant, web search, a cross-encoder and an LLM. This keeps development deterministic while preserving clean integration boundaries.
