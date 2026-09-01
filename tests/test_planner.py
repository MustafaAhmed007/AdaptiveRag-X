from adaptive_rag.models import Complexity, Intent
from adaptive_rag.planner import build_plan, profile_query

def test_current_query_routes_to_web():
    profile = profile_query("What is the latest status today?")
    assert profile.intent == Intent.CURRENT
    assert profile.freshness_required

def test_comparison_is_high_intelligence():
    plan = build_plan("Compare hybrid retrieval versus dense retrieval and explain the differences")
    assert plan.rerank
    assert plan.name == "adaptive_hybrid_rerank"

def test_short_question_is_fast():
    plan = build_plan("What is RAG?")
    assert plan.profile.complexity == Complexity.LOW
    assert plan.name == "dense_fast"
