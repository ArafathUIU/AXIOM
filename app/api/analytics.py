from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import case, desc, func, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.request_log import RequestLog
from app.schemas.analytics import (
    AnalyticsSummary,
    EndpointAnalytics,
    StatusCodeAnalytics,
)

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary", response_model=AnalyticsSummary)
def get_analytics_summary(db: Annotated[Session, Depends(get_db)]) -> AnalyticsSummary:
    total_requests = db.scalar(select(func.count()).select_from(RequestLog)) or 0
    error_count = db.scalar(
        select(func.count())
        .select_from(RequestLog)
        .where(RequestLog.status_code >= 400)
    ) or 0
    average_response_time = db.scalar(select(func.avg(RequestLog.response_time_ms))) or 0
    error_rate = (error_count / total_requests * 100) if total_requests else 0

    return AnalyticsSummary(
        total_requests=total_requests,
        error_count=error_count,
        error_rate=round(error_rate, 2),
        average_response_time_ms=round(float(average_response_time), 2),
    )


@router.get("/endpoints", response_model=list[EndpointAnalytics])
def get_endpoint_analytics(
    db: Annotated[Session, Depends(get_db)],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> list[EndpointAnalytics]:
    error_count = func.sum(case((RequestLog.status_code >= 400, 1), else_=0))
    statement = (
        select(
            RequestLog.method,
            RequestLog.path,
            func.count().label("request_count"),
            error_count.label("error_count"),
            func.avg(RequestLog.response_time_ms).label("average_response_time_ms"),
        )
        .group_by(RequestLog.method, RequestLog.path)
        .order_by(desc("request_count"))
        .limit(limit)
    )

    return [
        EndpointAnalytics(
            method=row.method,
            path=row.path,
            request_count=row.request_count,
            error_count=row.error_count,
            average_response_time_ms=round(float(row.average_response_time_ms), 2),
        )
        for row in db.execute(statement)
    ]


@router.get("/status-codes", response_model=list[StatusCodeAnalytics])
def get_status_code_analytics(
    db: Annotated[Session, Depends(get_db)],
) -> list[StatusCodeAnalytics]:
    statement = (
        select(
            RequestLog.status_code,
            func.count().label("count"),
        )
        .group_by(RequestLog.status_code)
        .order_by(RequestLog.status_code)
    )

    return [
        StatusCodeAnalytics(status_code=row.status_code, count=row.count)
        for row in db.execute(statement)
    ]
