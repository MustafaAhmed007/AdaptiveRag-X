from collections import Counter
import math
from .base import Retriever,tokenize
from ..models import Evidence
class BM25Retriever(Retriever):
    def __init__(self,k1=1.5,b=.75): self.k1=k1; self.b=b; self.docs=[]
    def add(self,documents): self.docs.extend(documents)
    def retrieve(self,query,top_k=5):
        if not self.docs:return []
        tokenized=[tokenize(d.text) for d in self.docs]; avg=sum(map(len,tokenized))/len(tokenized); q=set(tokenize(query)); N=len(self.docs); df=Counter(t for ts in tokenized for t in set(ts)); out=[]
        for d,ts in zip(self.docs,tokenized):
            tf=Counter(ts); score=0
            for term in q:
                if term not in tf: continue
                idf=math.log(1+(N-df[term]+.5)/(df[term]+.5)); score+=idf*(tf[term]*(self.k1+1))/(tf[term]+self.k1*(1-self.b+self.b*len(ts)/max(avg,1)))
            out.append((score,d))
        out.sort(key=lambda x:x[0],reverse=True); mx=out[0][0] if out else 1
        return [Evidence(document_id=d.id,text=d.text,score=score/mx if mx else 0,source=d.source,rank=i+1,metadata=d.metadata) for i,(score,d) in enumerate(out[:top_k])]
