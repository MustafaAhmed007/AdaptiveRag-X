import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "AdaptiveRAG-X")
    environment: str = os.getenv("ENVIRONMENT", "development")
    api_key: str = os.getenv("ADAPTIVE_RAG_API_KEY", "")
    llm_provider: str = os.getenv("LLM_PROVIDER", "mock")
    llm_model: str = os.getenv("LLM_MODEL", "gpt-4.1-mini")
    embedding_provider: str = os.getenv("EMBEDDING_PROVIDER", "hash")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    qdrant_url: str = os.getenv("QDRANT_URL", "")
    qdrant_collection: str = os.getenv("QDRANT_COLLECTION", "adaptive-rag")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///adaptive_rag.db")
    web_search_url: str = os.getenv("WEB_SEARCH_URL", "")
    max_requests_per_minute: int = int(os.getenv("MAX_REQUESTS_PER_MINUTE", "60"))


settings = Settings()
