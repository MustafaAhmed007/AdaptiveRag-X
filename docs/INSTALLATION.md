# Installation & Zero-Friction Start

AdaptiveRAG-X is designed so a new machine does not require a manual dependency-debugging session.

## One command

### macOS / Linux

```bash
./install.sh
source .venv/bin/activate
adaptive-rag-api
```

### Windows PowerShell

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\install.ps1
.\.venv\Scripts\adaptive-rag-api.exe
```

The installer:

1. verifies Python 3.11+;
2. creates an isolated `.venv`;
3. upgrades packaging tools;
4. installs the complete optional stack (`[all]`);
5. creates `.env` from `.env.example` when needed;
6. runs the test suite before reporting success.

No cloud credentials are required for the deterministic local baseline.

## Optional cloud intelligence

Set `LLM_PROVIDER` and `OPENAI_API_KEY` in `.env` when provider-backed generation is desired. Set `WEB_SEARCH_URL` to a compatible JSON search endpoint to enable cloud search.

## Multi-aspect auto-research

```bash
adaptive-rag research "Compare hybrid RAG and GraphRAG for production systems"
```

With a direct source:

```bash
adaptive-rag research "Summarize this specification" --url https://example.com/spec
```

With local evidence:

```bash
adaptive-rag research "What decisions are in these notes?" --file ./notes.md
```

The research layer expands a question into multiple evidence aspects, attempts optional cloud search, then supplements or replaces it with direct URLs and local files. A cloud outage therefore does not make the system unusable.

## API

Research endpoint:

```bash
curl -X POST http://127.0.0.1:8000/v1/research \
  -H 'content-type: application/json' \
  -d '{"question":"Compare hybrid and dense RAG","urls":[] ,"files":[] ,"top_k":5}'
```

## Architecture contract

`planner -> retrieval -> graph/web/research -> dedupe -> rerank -> evaluation -> bounded retry -> generation -> grounded response`

Research is an input-producing subsystem, not a replacement for the core adaptive RAG pipeline. This keeps retrieval, evidence, generation, evaluation, and external research independently replaceable.
