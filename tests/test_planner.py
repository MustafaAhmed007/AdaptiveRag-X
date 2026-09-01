from adaptive_rag.models import Complexity, Intent, RetrievalMode
from adaptive_rag.planner import build_plan, profile_query


def test_current_query_routes_to_web():
    profile = profile_query("What is the latest status today?")
    assert profile.intent is Intent.CURRENT
    assert profile.freshness_required
    assert RetrievalMode.WEB in build_plan("latest status today").modes


def test_comparison_is_adaptive():
    plan = build_plan("Compare hybrid retrieval versus dense retrieval and explain the differences")
    assert plan.rerank
    assert plan.profile.intent is Intent.COMPARISON


def test_short_question_is_fast():
    plan = build_plan("What is RAG?")
    assert plan.profile.complexity is Complexity.LOW
