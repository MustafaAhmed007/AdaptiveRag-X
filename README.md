# AdaptiveRAG-X

Production-oriented adaptive Retrieval-Augmented Generation reference system.

Core loop: `Query → Profile → Plan → Retrieve → Fuse → Rerank → Grade → Recover → Generate → Verify → Evaluate → Trace`.

Implemented: typed query intelligence; explainable routing; deterministic local retrieval; BM25; hybrid fusion; reranking; multi-hop decomposition; bounded query rewriting; evidence and groundedness evaluation; citations; prompt-injection gate; traces; cost accounting; FastAPI; provider boundary; Docker; CI; tests; architecture decisions; interview guide.

Quick start:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
uvicorn adaptive_rag.api:app --reload
```

Quality gates:

```bash
ruff check adaptive_rag tests
pytest -q
```

The core is deterministic and runs without API keys. Production integrations belong behind explicit provider boundaries and should only be documented as complete after implementation and tests exist. No benchmark numbers are fabricated.

License: MIT
