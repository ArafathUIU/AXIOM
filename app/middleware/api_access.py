from collections import defaultdict, deque
from time import monotonic

from fastapi import FastAPI, Request, Response
from starlette.responses import JSONResponse

from app.core.config import settings
from app.db.session import SessionLocal
from app.services.api_keys import find_active_api_key, mark_api_key_used

EXCLUDED_PREFIXES = ("/assets", "/docs", "/openapi.json", "/redoc")
EXCLUDED_PATHS = {"/health"}
_WINDOW_SECONDS = 60
_BUCKETS: dict[str, deque[float]] = defaultdict(deque)


def register_api_access_middleware(app: FastAPI) -> None:
    @app.middleware("http")
    async def api_access(request: Request, call_next) -> Response:  # type: ignore[no-untyped-def]
        if _is_excluded(request.url.path):
            return await call_next(request)

        raw_key = request.headers.get("x-api-key")
        principal = f"ip:{request.client.host if request.client else 'unknown'}"
        limit = settings.ip_rate_limit_per_minute

        if raw_key:
            with SessionLocal() as db:
                api_key = find_active_api_key(db, raw_key)
                if api_key is None:
                    return JSONResponse({"detail": "Invalid API key"}, status_code=401)
                mark_api_key_used(db, api_key)
                principal = f"key:{api_key.id}"
                limit = settings.api_key_rate_limit_per_minute

        allowed, remaining = _check_rate_limit(principal, limit)
        if not allowed:
            return JSONResponse(
                {"detail": "Rate limit exceeded"},
                status_code=429,
                headers={"X-RateLimit-Limit": str(limit), "X-RateLimit-Remaining": "0"},
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        return response


def _check_rate_limit(principal: str, limit: int) -> tuple[bool, int]:
    if not settings.enable_rate_limiting or limit <= 0:
        return True, max(limit, 0)

    now = monotonic()
    bucket = _BUCKETS[principal]
    while bucket and now - bucket[0] >= _WINDOW_SECONDS:
        bucket.popleft()
    if len(bucket) >= limit:
        return False, 0
    bucket.append(now)
    return True, max(limit - len(bucket), 0)


def _is_excluded(path: str) -> bool:
    return path in EXCLUDED_PATHS or any(path.startswith(prefix) for prefix in EXCLUDED_PREFIXES)
