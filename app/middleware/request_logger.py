from time import perf_counter

from fastapi import FastAPI, Request, Response
from sqlalchemy.exc import SQLAlchemyError

from app.db.session import SessionLocal
from app.models.request_log import RequestLog

EXCLUDED_PATHS = {"/health"}


def register_request_logger(app: FastAPI) -> None:
    @app.middleware("http")
    async def log_request(request: Request, call_next) -> Response:  # type: ignore[no-untyped-def]
        if request.url.path in EXCLUDED_PATHS:
            return await call_next(request)

        started_at = perf_counter()
        status_code = 500

        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        finally:
            response_time_ms = (perf_counter() - started_at) * 1000
            _store_request_log(request, status_code, response_time_ms)


def _store_request_log(
    request: Request,
    status_code: int,
    response_time_ms: float,
) -> None:
    db = SessionLocal()
    try:
        db.add(
            RequestLog(
                method=request.method,
                path=request.url.path,
                status_code=status_code,
                response_time_ms=response_time_ms,
                client_ip=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent"),
            )
        )
        db.commit()
    except SQLAlchemyError:
        db.rollback()
    finally:
        db.close()
