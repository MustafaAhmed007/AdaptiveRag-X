from .base import Retriever
from ..models import Evidence
from .rerank import SimpleReranker
class HybridRetriever(Retriever):
    def __init__(self,dense,sparse,dense_weight=.6,sparse_weight=.4): self.dense=dense; self.sparse=sparse; self.dw=dense_weight; self.sw=sparse_weight
    def add(self,documents): self.dense.add(documents); self.sparse.add(documents)
    def retrieve(self,query,top_k=5):
        merged={}
        for e in self.dense.retrieve(query,top_k*3): merged[e.document_id]=[e,self.dw*e.score]
        for e in self.sparse.retrieve(query,top_k*3):
            if e.document_id in merged: merged[e.document_id][1]+=self.sw*e.score
            else: merged[e.document_id]=[e,self.sw*e.score]
        ranked=[e.model_copy(update={'score':min(1,s)}) for e,s in merged.values()]; ranked.sort(key=lambda e:e.score,reverse=True)
        return [e.model_copy(update={'rank':i+1}) for i,e in enumerate(ranked[:top_k])]
