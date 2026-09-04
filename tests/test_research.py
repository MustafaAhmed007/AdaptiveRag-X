from adaptive_rag.research import MultiAspectResearch


def test_aspects_expand_for_comparison_and_freshness():
    aspects = MultiAspectResearch.aspects("Compare current hybrid RAG vs dense RAG")
    assert "comparison criteria" in aspects
    assert "trade-offs" in aspects
    assert "recent developments" in aspects


def test_local_fallback(tmp_path):
    source = tmp_path / "notes.md"
    source.write_text("Adaptive retrieval chooses a strategy from query intent.", encoding="utf-8")
    report = MultiAspectResearch().run("What is adaptive retrieval?", files=[str(source)])
    assert report.sources[0].kind == "local"
    assert report.evidence
    assert not report.warnings or "cloud search" not in report.warnings[0]
