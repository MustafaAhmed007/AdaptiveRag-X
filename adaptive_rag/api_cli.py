from __future__ import annotations

import uvicorn

from .config import settings


def main() -> None:
    uvicorn.run("adaptive_rag.api:app", host=settings.host, port=settings.port, reload=False)
