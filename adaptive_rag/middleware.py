from collections import defaultdict, deque
from time import monotonic

from fastapi import Request
from fastapi.responses import JSONResponse

from .config import settings


class RateLimiter:
    def __init__(self, limit: int = 60, window_seconds: int = 60):
        self.limit = limit
        self.window = window_seconds
        self.hits: dict[str, deque[float]] = defaultdict(deque)

    def check(self, key: str) -> bool:
        now = monotonic()
        bucket = self.hits[key]

        while bucket and now - bucket[0] >= self.window:
            bucket.popleft()

        if len(bucket) >= self.limit:
            return False

        bucket.append(now)
        return True


limiter = RateLimiter(settings.max_requests_per_minute)


async def auth_and_rate_limit(request: Request):
    if request.url.path == "/health":
        return None

    if not settings.api_key:
        return JSONResponse(
            status_code=503,
            content={"detail": "API authentication is not configured"},
        )

    supplied_key = request.headers.get("x-api-key")

    if supplied_key != settings.api_key:
        return JSONResponse(
            status_code=401,
            content={"detail": "invalid API key"},
        )

    client_ip = request.client.host if request.client else "unknown"

    if not limiter.check(client_ip):
        return JSONResponse(
            status_code=429,
            content={"detail": "rate limit exceeded"},
        )

    return None