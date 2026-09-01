def rewrite_query(query:str,attempt:int)->str:
    suffix=['',' exact terminology and named entities',' specific evidence, definitions, and relationships'][min(attempt,2)]
    return query.strip()+suffix

def decompose_query(query:str)->list[str]:
    parts=[p.strip(' ?') for p in query.replace(' and ',';').replace(' versus ',';').split(';') if p.strip()]
    return parts if len(parts)>1 else [query]

def build_citations(evidence):
    from .models import Citation
    return [Citation(document_id=e.document_id,source=e.source,span=e.text[:240]) for e in evidence]
