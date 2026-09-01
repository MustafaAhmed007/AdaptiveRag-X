import re

from .models import Evaluation, Evidence


def evaluate_evidence(evidence: list[Evidence]) -> Evaluation:
    scores = [item.score for item in evidence]
    relevance = sum(scores) / len(scores) if scores else 0.0
    precision = sum(score >= 0.35 for score in scores) / len(scores) if scores else 0.0
    recall = min(1.0, len(evidence) / 3) if evidence else 0.0
    groundedness = relevance
    citation_coverage = 1.0 if evidence else 0.0
    overall = sum((relevance, precision, recall, groundedness, citation_coverage)) / 5
    return Evaluation(
        retrieval_relevance=relevance,
        context_precision=precision,
        context_recall=recall,
        groundedness=groundedness,
        citation_coverage=citation_coverage,
        overall=overall,
        grounded=bool(evidence) and overall >= 0.35,
    )


def answer_grounded(answer: str, evidence: list[Evidence]) -> float:
    if not evidence or not answer.strip():
        return 0.0
    answer_tokens = set(re.findall(r"[a-zA-Z0-9]+", answer.lower()))
    evidence_tokens = set(re.findall(r"[a-zA-Z0-9]+", " ".join(item.text for item in evidence).lower()))
    return min(1.0, len(answer_tokens & evidence_tokens) / max(len(answer_tokens), 1) * 1.5)
