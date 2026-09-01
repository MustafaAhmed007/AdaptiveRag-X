from collections import defaultdict, deque
from time import monotonic

from fastapi import HTTPException, Request

from .config import settings


class RateLimiter:
    def __init__(self, limit: int = 60, window_seconds: int = 60):
        self.limit = limit
        self.window = window_seconds
        self.hits: dict[str, deque[float]] = defaultdict(deque)

    def check(self, key: str) -> None:
        now = monotonic()
        bucket = self.hits[key]
        while bucket and now - bucket[0] >= self.window:
            bucket.popleft()
        if len(bucket) >= self.limit:
            raise HTTPException(status_code=429, detail="rate limit exceeded")
        bucket.append(now)


limiter = RateLimiter(settings.max_requests_per_minute)


async def auth_and_rate_limit(request: Request) -> None:
    if request.url.path == "/health":
        return
    if settings.api_key and request.headers.get("x-api-key") != settings.api_key:
        raise HTTPException(status_code=401, detail="invalid API key")
    limiter.check(request.client.host if request.client else "unknown")
