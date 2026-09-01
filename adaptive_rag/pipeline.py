from uuid import uuid4
from .evaluation import evaluate_evidence
from .models import Citation, QueryResponse
from .observability import Trace
from .planner import build_plan
from .security import SecurityGate

class MockGenerator:
    """Provider-neutral generator for local tests; replace via dependency injection."""
    def generate(self, query: str, evidence) -> str:
        if not evidence:
            return "I do not have enough evidence in the indexed knowledge to answer that reliably."
        snippets = " ".join(e.text for e in evidence[:3])
        return f"Based on the retrieved evidence: {snippets}"

class AdaptivePipeline:
    def __init__(self, retriever, reranker=None, generator=None, security=None):
        self.retriever = retriever
        self.reranker = reranker
        self.generator = generator or MockGenerator()
        self.security = security or SecurityGate()

    def run(self, query: str, top_k: int = 5) -> QueryResponse:
        allowed, reason = self.security.inspect(query)
        if not allowed:
            raise ValueError(f"request blocked: {reason}")
        plan = build_plan(query, top_k)
        trace = Trace(strategy=plan.name)
        trace.event("query_profile", profile=plan.profile.model_dump())
        evidence = []
        attempts = 0
        for attempts in range(1, plan.max_attempts + 1):
            evidence = self.retriever.retrieve(query, plan.top_k)
            trace.event("retrieval", attempt=attempts, count=len(evidence))
            if plan.rerank and self.reranker:
                evidence = self.reranker.rerank(query, evidence, plan.top_k)
                trace.event("rerank", count=len(evidence))
            evaluation = evaluate_evidence(evidence)
            trace.event("evidence_eval", quality=evaluation.evidence_quality, grounded=evaluation.grounded)
            if evaluation.grounded or attempts == plan.max_attempts:
                break
            query = f"{query} with precise terminology and supporting evidence"
            trace.event("query_rewrite", attempt=attempts + 1)
        answer = self.generator.generate(query, evidence)
        citations = [Citation(document_id=e.document_id, source=e.source, span=e.text[:180]) for e in evidence]
        confidence = evaluate_evidence(evidence).evidence_quality
        trace.attempts = attempts
        return QueryResponse(answer=answer, strategy=plan.name, confidence=confidence,
                             citations=citations, trace_id=trace.trace_id, attempts=attempts,
                             estimated_cost_usd=trace.estimated_cost_usd)
