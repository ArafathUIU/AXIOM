from datetime import datetime
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
def get_analytics_summary(
    db: Annotated[Session, Depends(get_db)],
    start_time: datetime | None = None,
    end_time: datetime | None = None,
) -> AnalyticsSummary:
    filters = _time_filters(start_time, end_time)
    total_requests = db.scalar(
        select(func.count()).select_from(RequestLog).where(*filters)
    ) or 0
    error_count = db.scalar(
        select(func.count())
        .select_from(RequestLog)
        .where(RequestLog.status_code >= 400)
        .where(*filters)
    ) or 0
    average_response_time = db.scalar(
        select(func.avg(RequestLog.response_time_ms)).where(*filters)
    ) or 0
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
    start_time: datetime | None = None,
    end_time: datetime | None = None,
) -> list[EndpointAnalytics]:
    filters = _time_filters(start_time, end_time)
    error_count = func.sum(case((RequestLog.status_code >= 400, 1), else_=0))
    statement = (
        select(
            RequestLog.method,
            RequestLog.path,
            func.count().label("request_count"),
            error_count.label("error_count"),
            func.avg(RequestLog.response_time_ms).label("average_response_time_ms"),
        )
        .where(*filters)
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
    start_time: datetime | None = None,
    end_time: datetime | None = None,
) -> list[StatusCodeAnalytics]:
    filters = _time_filters(start_time, end_time)
    statement = (
        select(
            RequestLog.status_code,
            func.count().label("count"),
        )
        .where(*filters)
        .group_by(RequestLog.status_code)
        .order_by(RequestLog.status_code)
    )

    return [
        StatusCodeAnalytics(status_code=row.status_code, count=row.count)
        for row in db.execute(statement)
    ]


@router.get("/slowest-endpoints", response_model=list[EndpointAnalytics])
def get_slowest_endpoint_analytics(
    db: Annotated[Session, Depends(get_db)],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
) -> list[EndpointAnalytics]:
    filters = _time_filters(start_time, end_time)
    error_count = func.sum(case((RequestLog.status_code >= 400, 1), else_=0))
    average_response_time = func.avg(RequestLog.response_time_ms)
    statement = (
        select(
            RequestLog.method,
            RequestLog.path,
            func.count().label("request_count"),
            error_count.label("error_count"),
            average_response_time.label("average_response_time_ms"),
        )
        .where(*filters)
        .group_by(RequestLog.method, RequestLog.path)
        .order_by(desc(average_response_time))
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


def _time_filters(start_time: datetime | None, end_time: datetime | None) -> list[object]:
    filters = []
    if start_time is not None:
        filters.append(RequestLog.created_at >= start_time)
    if end_time is not None:
        filters.append(RequestLog.created_at <= end_time)
    return filters
