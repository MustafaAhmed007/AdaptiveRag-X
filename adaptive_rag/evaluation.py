from dataclasses import dataclass
from .models import Evidence

@dataclass(frozen=True)
class Evaluation:
    evidence_quality: float
    citation_coverage: float
    grounded: bool


def evaluate_evidence(evidence: list[Evidence], threshold: float = 0.65) -> Evaluation:
    if not evidence:
        return Evaluation(0.0, 0.0, False)
    quality = sum(e.score for e in evidence) / len(evidence)
    grounded = quality >= threshold
    return Evaluation(quality, 1.0 if grounded else 0.0, grounded)
