# Architecture

## Decision model

AdaptiveRAG-X treats retrieval as a policy decision. The planner estimates intent, complexity and freshness requirements before selecting a strategy.

| Query profile | Default strategy | Why |
|---|---|---|
| short factual | dense_fast | minimize latency and cost |
| explanatory | hybrid | improve lexical + semantic coverage |
| comparison / multi-hop | adaptive_hybrid_rerank | broader candidate set and precision ranking |
| freshness-sensitive | web_hybrid | external/current evidence is required |

## Recovery loop

Evidence quality is evaluated before generation. If evidence is weak, the system rewrites the retrieval query and retries within a bounded attempt budget. This prevents unbounded agent loops.

## Provider boundaries

The core pipeline depends on `Retriever`, `Reranker`, and generator contracts rather than vendor SDKs. This allows Qdrant, Elasticsearch/BM25, cross-encoders, hosted LLMs or local models to be introduced without rewriting orchestration.

## Production extension points

1. Replace `InMemoryRetriever` with a vector database adapter.
2. Add a real sparse retriever and reciprocal-rank fusion.
3. Add a cross-encoder reranker.
4. Add web and graph tools behind permissioned interfaces.
5. Export traces to OpenTelemetry and metrics to Prometheus.
6. Persist evaluation traces for regression analysis.
