from .base import Retriever,lexical_score
from ..models import Evidence
class InMemoryRetriever(Retriever):
    def __init__(self,documents=None): self.docs=list(documents or [])
    def add(self,documents): self.docs.extend(documents)
    def retrieve(self,query,top_k=5):
        ranked=sorted(((lexical_score(query,d.text),d) for d in self.docs),key=lambda x:x[0],reverse=True)
        return [Evidence(document_id=d.id,text=d.text,score=min(1,s),source=d.source,rank=i+1,metadata=d.metadata) for i,(s,d) in enumerate(ranked[:top_k])]
InMemoryDenseLike=InMemoryRetriever
