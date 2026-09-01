from urllib.request import Request, urlopen
import json

from ..models import Evidence


class WebRetriever:
    """Configurable JSON search adapter. Set WEB_SEARCH_URL to a compatible endpoint."""

    def __init__(self, endpoint: str, timeout: float = 8.0):
        self.endpoint = endpoint
        self.timeout = timeout

    def retrieve(self, query: str, top_k: int = 5) -> list[Evidence]:
        if not self.endpoint:
            return []
        separator = "&" if "?" in self.endpoint else "?"
        request = Request(f"{self.endpoint}{separator}q={query}&limit={top_k}")
        with urlopen(request, timeout=self.timeout) as response:
            payload = json.load(response)
        results = payload.get("results", payload if isinstance(payload, list) else [])
        return [
            Evidence(
                document_id=str(item.get("id", index)),
                text=item.get("text", item.get("snippet", "")),
                score=float(item.get("score", 0.5)),
                source=item.get("url", "web"),
                rank=index,
                metadata=item,
            )
            for index, item in enumerate(results[:top_k], start=1)
        ]
