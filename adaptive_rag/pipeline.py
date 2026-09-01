from .evaluation import answer_grounded, evaluate_evidence
from .models import Evidence, QueryResponse
from .observability import Trace
from .planner import build_plan
from .providers import build_generator
from .query import build_citations, decompose_query, rewrite_query
from .retrieval.graph import EntityGraphRetriever
from .retrieval.hybrid import HybridRetriever
from .retrieval.memory import InMemoryRetriever
from .retrieval.rerank import ScoreReranker
from .retrieval.sparse import BM25Retriever
from .retrieval.web import WebRetriever
from .security import SecurityGate


class AdaptivePipeline:
    def __init__(self, retriever=None, reranker=None, generator=None, security=None, web_retriever=None):
        self.retriever = retriever or HybridRetriever(InMemoryRetriever(), BM25Retriever())
        self.graph = EntityGraphRetriever()
        self.reranker = reranker or ScoreReranker()
        self.generator = generator or build_generator()
        self.security = security or SecurityGate()
        self.web = web_retriever or WebRetriever("")

    def add_documents(self, documents) -> None:
        self.retriever.add(documents)
        self.graph.add(documents)

    def run(self, query: str, top_k: int = 5) -> QueryResponse:
        allowed, reason = self.security.inspect(query)
        if not allowed:
            raise ValueError(f"request blocked: {reason}")
        original = query
        plan = build_plan(query, top_k)
        trace = Trace(plan.name)
        evidence: list[Evidence] = []
        attempt = 0
        for attempt in range(1, plan.max_attempts + 1):
            subqueries = decompose_query(query) if plan.profile.multi_hop else [query]
            pool: list[Evidence] = []
            for subquery in subqueries:
                pool.extend(self.retriever.retrieve(subquery, plan.top_k))
                if plan.profile.multi_hop:
                    pool.extend(self.graph.retrieve(subquery, plan.top_k))
            if plan.profile.freshness_required:
                pool.extend(self.web.retrieve(query, plan.top_k))
            evidence = list({item.document_id: item for item in pool}.values())
            if plan.rerank:
                evidence = self.reranker.rerank(original, evidence, plan.top_k)
            evaluation = evaluate_evidence(evidence)
            trace.event("attempt", attempt=attempt, evidence=len(evidence), quality=evaluation.overall)
            if evaluation.grounded or attempt == plan.max_attempts:
                break
            query = rewrite_query(original, attempt)
            trace.event("rewrite", query=query)
        answer = self.generator.generate(original, evidence)
        grounded = answer_grounded(answer, evidence)
        trace.attempts = attempt
        trace.finish()
        evaluation = evaluate_evidence(evidence)
        return QueryResponse(
            answer=answer,
            strategy=plan.name,
            confidence=min(1.0, 0.5 * evaluation.overall + 0.5 * grounded),
            citations=build_citations(evidence),
            trace_id=trace.trace_id,
            attempts=attempt,
            estimated_cost_usd=trace.estimated_cost_usd,
        )
