import re
from .models import Complexity, Intent, Plan, QueryProfile, RetrievalMode

def profile_query(query:str)->QueryProfile:
    q=query.lower(); words=re.findall(r'\w+',q)
    current=any(x in q for x in ('today','latest','current','recent','this month','2026','now'))
    multi=any(x in q for x in ('and also','across','both','between','which companies','compare')) or len(words)>25
    if any(x in q for x in ('compare','versus',' vs ','difference between')): intent=Intent.COMPARISON
    elif multi: intent=Intent.MULTI_HOP
    elif current: intent=Intent.CURRENT
    elif any(x in q for x in ('how','why','explain','overview','analyze')): intent=Intent.EXPLORATORY
    else: intent=Intent.FACTUAL
    complexity=Complexity.HIGH if multi or len(words)>30 else Complexity.MEDIUM if len(words)>10 or intent in (Intent.COMPARISON,Intent.EXPLORATORY) else Complexity.LOW
    return QueryProfile(intent=intent,complexity=complexity,freshness_required=current,multi_hop=multi,risk='medium' if current else 'low')

def build_plan(query:str,top_k:int=5)->Plan:
    p=profile_query(query)
    if p.freshness_required: modes=[RetrievalMode.WEB,RetrievalMode.HYBRID]
    elif p.multi_hop: modes=[RetrievalMode.HYBRID,RetrievalMode.GRAPH]
    elif p.complexity==Complexity.LOW: modes=[RetrievalMode.DENSE]
    else: modes=[RetrievalMode.HYBRID]
    return Plan(name='adaptive_'+'_'.join(m.value for m in modes),profile=p,modes=modes,top_k=top_k,max_attempts=3 if p.complexity==Complexity.HIGH else 2,rerank=p.complexity!=Complexity.LOW)
