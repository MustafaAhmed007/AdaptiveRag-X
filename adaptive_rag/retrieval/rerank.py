from ..models import Evidence
class ScoreReranker:
    def rerank(self,query,evidence,top_k=5):
        q=set(query.lower().split())
        def score(e): return .65*e.score+.35*(len(q & set(e.text.lower().split()))/max(1,len(q)))
        ranked=sorted(evidence,key=score,reverse=True)[:top_k]
        return [e.model_copy(update={'score':min(1,score(e)),'rank':i+1}) for i,e in enumerate(ranked)]
SimpleReranker=ScoreReranker
