# ADR 0001 — Adaptive routing

## Context

A single retrieval strategy is inefficient across factual, exploratory, comparison, multi-hop and freshness-sensitive queries.

## Decision

Classify the query into a small typed profile and select a bounded strategy before retrieval.

## Consequences

**Positive:** lower expected latency/cost for simple queries and more retrieval depth for complex queries.

**Trade-off:** the classifier can be wrong, so routing decisions must be observable and benchmarked.

## Validation

The repository includes deterministic routing tests and a benchmark smoke test. Future provider-backed experiments should compare routing against fixed baselines.
