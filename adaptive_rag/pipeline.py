from .models import QueryResponse
from .planner import build_plan
from .evaluation import evaluate_evidence,answer_grounded
from .observability import Trace
from .security import SecurityGate
from .retrieval.memory import InMemoryRetriever
from .retrieval.sparse import BM25Retriever
from .retrieval.hybrid import HybridRetriever
from .retrieval.rerank import ScoreReranker
from .providers import MockGenerator
from .query import rewrite_query,decompose_query,build_citations
class AdaptivePipeline:
    def __init__(self,retriever=None,reranker=None,generator=None,security=None):
        self.retriever=retriever or HybridRetriever(InMemoryRetriever(),BM25Retriever()); self.reranker=reranker or ScoreReranker(); self.generator=generator or MockGenerator(); self.security=security or SecurityGate()
    def add_documents(self,documents): self.retriever.add(documents)
    def run(self,query:str,top_k:int=5)->QueryResponse:
        allowed,reason=self.security.inspect(query)
        if not allowed: raise ValueError('request blocked: '+reason)
        original=query; plan=build_plan(query,top_k); trace=Trace(plan.name); evidence=[]
        for attempt in range(1,plan.max_attempts+1):
            subs=decompose_query(query) if plan.profile.multi_hop else [query]; pool=[]
            for sq in subs: pool.extend(self.retriever.retrieve(sq,plan.top_k))
            evidence=list({e.document_id:e for e in pool}.values())
            if plan.rerank: evidence=self.reranker.rerank(original,evidence,plan.top_k)
            ev=evaluate_evidence(evidence); trace.event('attempt',attempt=attempt,evidence=len(evidence),quality=ev.overall)
            if ev.grounded or attempt==plan.max_attempts: break
            query=rewrite_query(original,attempt); trace.event('rewrite',query=query)
        answer=self.generator.generate(original,evidence); grounded=answer_grounded(answer,evidence); trace.attempts=attempt; trace.finish()
        ev=evaluate_evidence(evidence)
        return QueryResponse(answer=answer,strategy=plan.name,confidence=min(1,.5*ev.overall+.5*grounded),citations=build_citations(evidence),trace_id=trace.trace_id,attempts=attempt,estimated_cost_usd=trace.estimated_cost_usd)
