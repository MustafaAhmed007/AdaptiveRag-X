from pathlib import Path
from uuid import uuid4
from .models import Document

def chunk_text(text:str,size:int=800,overlap:int=120)->list[str]:
    if size<=overlap: raise ValueError('size must exceed overlap')
    words=text.split(); width=max(1,size//5); step=max(1,width-overlap//5); out=[]; start=0
    while start<len(words):
        out.append(' '.join(words[start:start+width]))
        if start+width>=len(words): break
        start+=step
    return [x for x in out if x.strip()]

def ingest_text(text,source='upload',metadata=None):
    return [Document(id=str(uuid4()),text=x,source=source,metadata=metadata or {}) for x in chunk_text(text)]

def ingest_markdown(text,source='markdown'):
    sections=text.split('\n# ')
    return [Document(id=str(uuid4()),text=s.strip(),source=source,metadata={'format':'markdown'}) for s in sections if s.strip()]

def load_file(path:str):
    p=Path(path); return ingest_text(p.read_text(encoding='utf-8'),str(p))
