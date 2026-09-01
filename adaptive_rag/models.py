from enum import Enum
from pydantic import BaseModel, Field

class Intent(str, Enum):
    FACTUAL = "factual"
    EXPLORATORY = "exploratory"
    COMPARISON = "comparison"
    MULTI_HOP = "multi_hop"
    CURRENT = "current"

class Complexity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class QueryProfile(BaseModel):
    intent: Intent = Intent.FACTUAL
    complexity: Complexity = Complexity.LOW
    freshness_required: bool = False
    multi_hop: bool = False
    risk: str = "low"

class Document(BaseModel):
    id: str
    text: str
    source: str = "memory"
    metadata: dict[str, str] = Field(default_factory=dict)

class Evidence(BaseModel):
    document_id: str
    text: str
    score: float = Field(ge=0, le=1)
    source: str

class Citation(BaseModel):
    document_id: str
    source: str
    span: str

class QueryRequest(BaseModel):
    query: str = Field(min_length=1, max_length=8000)
    top_k: int = Field(default=5, ge=1, le=50)

class QueryResponse(BaseModel):
    answer: str
    strategy: str
    confidence: float
    citations: list[Citation]
    trace_id: str
    attempts: int
    estimated_cost_usd: float
