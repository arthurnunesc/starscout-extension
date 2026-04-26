from dataclasses import dataclass
from time import monotonic

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response


@dataclass
class _Bucket:
    window_started_at: float
    count: int


class RepoIntegrityRateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_per_minute: int) -> None:
        super().__init__(app)
        self._requests_per_minute = requests_per_minute
        self._buckets: dict[str, _Bucket] = {}

    async def dispatch(self, request: Request, call_next) -> Response:
        if self._requests_per_minute <= 0 or not _is_repo_integrity_request(request):
            return await call_next(request)

        client_host = request.client.host if request.client else "unknown"
        now = monotonic()
        bucket = self._buckets.get(client_host)
        if bucket is None or now - bucket.window_started_at >= 60:
            self._buckets[client_host] = _Bucket(window_started_at=now, count=1)
            return await call_next(request)

        if bucket.count >= self._requests_per_minute:
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded."},
                headers={"Retry-After": str(max(1, int(60 - (now - bucket.window_started_at))))},
            )

        bucket.count += 1
        return await call_next(request)


def _is_repo_integrity_request(request: Request) -> bool:
    return request.method == "GET" and request.url.path.endswith("/star-integrity")
