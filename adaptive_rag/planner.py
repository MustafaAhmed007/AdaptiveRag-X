import re

from .models import Complexity, Intent, Plan, QueryProfile, RetrievalMode


def profile_query(query: str) -> QueryProfile:
    text = query.lower()
    freshness = bool(re.search(r"\b(latest|today|current|now|recent|this week|2026)\b", text))
    multi_hop = bool(re.search(r"\b(and|then|after|because|relationship|how.*affect|compare.*and)\b", text))
    comparison = bool(re.search(r"\b(compare|versus|vs\.?|difference|better)\b", text))
    exploratory = bool(re.search(r"\b(explain|why|how does|overview|explore|deep dive)\b", text))
    intent = (
        Intent.CURRENT if freshness else
        Intent.MULTI_HOP if multi_hop else
        Intent.COMPARISON if comparison else
        Intent.EXPLORATORY if exploratory else Intent.FACTUAL
    )
    complexity = Complexity.HIGH if multi_hop or len(text.split()) > 24 else Complexity.MEDIUM if len(text.split()) > 10 else Complexity.LOW
    return QueryProfile(
        intent=intent,
        complexity=complexity,
        freshness_required=freshness,
        multi_hop=multi_hop,
        requires_retrieval=True,
    )


def build_plan(query: str, top_k: int = 5) -> Plan:
    profile = profile_query(query)
    modes: list[RetrievalMode]
    if profile.freshness_required:
        modes = [RetrievalMode.WEB, RetrievalMode.HYBRID]
    elif profile.multi_hop:
        modes = [RetrievalMode.HYBRID, RetrievalMode.GRAPH]
    elif profile.complexity is Complexity.LOW:
        modes = [RetrievalMode.DENSE]
    else:
        modes = [RetrievalMode.HYBRID]
    attempts = 3 if profile.complexity is Complexity.HIGH else 2
    return Plan(
        name="adaptive_" + "_".join(mode.value for mode in modes),
        profile=profile,
        modes=modes,
        top_k=top_k,
        max_attempts=attempts,
        rerank=profile.complexity is not Complexity.LOW,
    )
