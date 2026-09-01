from fastapi import FastAPI,HTTPException
from .models import QueryRequest,QueryResponse
from .pipeline import AdaptivePipeline
from .services import ingest_text
app=FastAPI(title='AdaptiveRAG-X',version='1.0.0',description='Self-evaluating adaptive RAG platform')
pipeline=AdaptivePipeline()
@app.get('/health')
def health(): return {'status':'ok','service':'adaptive-rag-x'}
@app.post('/v1/documents')
def add_document(payload:dict):
    text=str(payload.get('text','')).strip()
    if not text: raise HTTPException(400,'text is required')
    docs=ingest_text(text,payload.get('source','api'),payload.get('metadata',{})); pipeline.add_documents(docs)
    return {'indexed':len(docs),'document_ids':[d.id for d in docs]}
@app.post('/v1/query',response_model=QueryResponse)
def query(req:QueryRequest):
    try:return pipeline.run(req.query,req.top_k)
    except ValueError as exc: raise HTTPException(400,str(exc)) from exc
