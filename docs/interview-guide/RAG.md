# RAG interview guide

## What problem does RAG solve?

RAG supplies external evidence to a language model at inference time. It can reduce dependence on memorized knowledge and make answers traceable to retrieved sources.

## Why hybrid retrieval?

Dense retrieval captures semantic similarity; lexical retrieval is strong for exact terms, identifiers and rare strings. Fusion combines their strengths.

## Why reranking?

Initial retrieval is optimized for recall. A reranker can spend more compute on a smaller candidate set to improve precision before generation.

## Why adaptive routing?

Not every query needs the same retrieval depth. Routing makes latency, cost and evidence requirements explicit.

## What can fail?

- wrong route
- poor chunking
- missing evidence
- noisy candidate set
- weak reranker
- hallucinated synthesis
- citation mismatch
- stale external data

## Strong interview answer

A production RAG system should be treated as a measurable information-retrieval system, not simply an LLM prompt. I would define retrieval and generation metrics separately, trace every decision, establish fixed baselines, and only add agentic complexity when experiments demonstrate a quality benefit.
