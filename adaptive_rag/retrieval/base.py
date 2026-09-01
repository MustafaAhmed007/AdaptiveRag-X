from abc import ABC,abstractmethod
from collections import Counter
from ..models import Document,Evidence
class Retriever(ABC):
    @abstractmethod
    def add(self,documents:list[Document])->None: ...
    @abstractmethod
    def retrieve(self,query:str,top_k:int=5)->list[Evidence]: ...
def tokenize(text): return [x.lower() for x in text.replace('_',' ').split() if x]
def lexical_score(query,text):
    q=Counter(tokenize(query)); d=Counter(tokenize(text))
    return sum(min(q[t],d[t]) for t in q)/max(1,sum(q.values()))
