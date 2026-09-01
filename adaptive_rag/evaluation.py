import re
from .models import Evaluation,Evidence
def evaluate_evidence(evidence:list[Evidence])->Evaluation:
    scores=[e.score for e in evidence]; relevance=sum(scores)/len(scores) if scores else 0
    precision=sum(s>=.45 for s in scores)/len(scores) if scores else 0; recall=min(1,max(scores)*1.15) if scores else 0
    grounded=min(1,.55*relevance+.45*precision); citation=min(1,len({e.document_id for e in evidence})/max(1,min(3,len(evidence))))
    overall=.25*relevance+.2*precision+.2*recall+.25*grounded+.1*citation
    return Evaluation(retrieval_relevance=relevance,context_precision=precision,context_recall=recall,groundedness=grounded,citation_coverage=citation,overall=overall,grounded=grounded>=.5)
def answer_grounded(answer:str,evidence:list[Evidence])->float:
    if not answer or not evidence:return 0
    aw=set(re.findall(r'\w+',answer.lower())); ew=set(re.findall(r'\w+',' '.join(e.text for e in evidence).lower()))
    return len(aw&ew)/max(1,len(aw))
