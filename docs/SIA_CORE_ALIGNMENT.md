# SIA CORE Ω — Portfolio Alignment

## Purpose

AdaptiveRAG-X is a domain implementation of the portfolio-wide SIA CORE Ω operating architecture. The generic kernel is not the RAG product itself; it is the repeatable loop:

**objective → context/research → evidence → strategy → execution → verification → outcome → learning → next decision**

## Universal contract

| Capability | Status | Domain implementation |
|---|---|---|
| Objective / outcome contract | Partial | Query intent and retrieval-quality objectives; add explicit business outcome contracts for production use |
| Evidence + provenance | Implemented | Retrieval evidence, citations, grounding and quality metrics |
| Multi-aspect research | Implemented | Query profiling, web retrieval, hybrid/graph paths |
| Deterministic core | Implemented | Local retrieval, BM25, fusion, bounded retries, evaluation |
| Intelligence/provider boundary | Implemented | Generation and embedding provider interfaces |
| Economic routing | Partial | Cost signals exist; make value-aware escalation a first-class policy |
| Orchestration | Implemented | Adaptive planner + pipeline |
| Verification/release gates | Implemented | Retrieval relevance, precision/recall, groundedness, citation coverage |
| Security/adversarial lane | Implemented | Prompt-injection gate; expand to systematic adversarial suite |
| Runtime verification | Partial | API/test execution exists; add production smoke contract |
| Telemetry | Implemented | Timing/traces/cost signals |
| Benchmarking | Implemented | Routing and quality benchmark harness |
| Experimentation | Partial | Benchmark/evaluation loop; add formal champion/challenger promotion |
| Outcome measurement | Partial | Retrieval/grounding outcomes; add downstream task/business outcomes |
| Causal learning | Planned | Add intervention/control/outcome contracts where measurable |
| Genome / failure memory | Partial | Evaluation history exists; normalize reusable failure/repair rules |
| One-click bootstrap / doctor | Partial | Existing venv quick start; standardize cross-platform setup + doctor |
| Artifact evidence trail | Implemented | Evaluation reports and structured outputs |
| Adapter boundaries | Implemented | Qdrant, web, reranker, graph and provider adapters |

## Domain boundary

RAG-specific capabilities remain outside the universal kernel: query profiling, retrieval strategy selection, BM25/dense/hybrid retrieval, graph retrieval, reranking, grounding and citation generation.

## Non-negotiables

1. Search results are evidence candidates, not truth.
2. Weak evidence must be visible and may trigger bounded recovery.
3. No uncontrolled agent loops.
4. External providers remain replaceable.
5. Quality, latency and cost are evaluated together.
6. Production claims require reproducible evidence.

## Target end state

The repo should consume a shared SIA CORE Ω contract while retaining its RAG ontology and execution modules. Do not duplicate generic infrastructure when a portfolio kernel becomes available.
