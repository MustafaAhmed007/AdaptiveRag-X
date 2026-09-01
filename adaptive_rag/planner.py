"""Deterministic query intelligence and adaptive strategy planning."""

import re
from dataclasses import dataclass
from .models import Complexity, Intent, QueryProfile

@dataclass(frozen=True)
class Plan:
    name: str
    profile: QueryProfile
    top_k: int
    rerank: bool
    max_attempts: int


def profile_query(query: str) -> QueryProfile:
    q = query.lower()
    words = q.split()
    current = any(x in q for x in ("today", "latest", "current", "this week", "recent"))
    multi = any(x in q for x in ("and", "both", "across", "relationship", "which ... also")) and len(words) > 8
    comparison = bool(re.search(r"\b(compare|versus|vs\.?|difference|better than)\b", q))
    exploratory = bool(re.search(r"\b(explain|overview|why|how does|what are the)\b", q))
    if current:
        intent = Intent.CURRENT
    elif multi:
        intent = Intent.MULTI_HOP
    elif comparison:
        intent = Intent.COMPARISON
    elif exploratory:
        intent = Intent.EXPLORATORY
    else:
        intent = Intent.FACTUAL
    complexity = Complexity.HIGH if len(words) > 35 or multi else Complexity.MEDIUM if len(words) > 12 else Complexity.LOW
    return QueryProfile(intent=intent, complexity=complexity, freshness_required=current, multi_hop=multi)


def build_plan(query: str, top_k: int = 5) -> Plan:
    profile = profile_query(query)
    if profile.intent == Intent.CURRENT:
        name = "web_hybrid"
    elif profile.intent in (Intent.COMPARISON, Intent.MULTI_HOP):
        name = "adaptive_hybrid_rerank"
    elif profile.complexity == Complexity.LOW:
        name = "dense_fast"
    else:
        name = "hybrid"
    return Plan(name=name, profile=profile, top_k=top_k, rerank=profile.complexity != Complexity.LOW, max_attempts=2)
