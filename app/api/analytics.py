from datetime import datetime
from math import ceil
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import case, desc, func, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.request_log import RequestLog
from app.schemas.analytics import (
    AnalyticsSummary,
    EndpointAnalytics,
    LatencyPercentiles,
    StatusCodeAnalytics,
    StatusCodeFamilyAnalytics,
    TrafficBucket,
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


@router.get("/status-code-families", response_model=list[StatusCodeFamilyAnalytics])
def get_status_code_family_analytics(
    db: Annotated[Session, Depends(get_db)],
    start_time: datetime | None = None,
    end_time: datetime | None = None,
) -> list[StatusCodeFamilyAnalytics]:
    statement = select(RequestLog.status_code).where(*_time_filters(start_time, end_time))
    families = {"1xx": 0, "2xx": 0, "3xx": 0, "4xx": 0, "5xx": 0}

    for status_code in db.scalars(statement):
        family = f"{status_code // 100}xx"
        if family in families:
            families[family] += 1

    return [
        StatusCodeFamilyAnalytics(family=family, count=count)
        for family, count in families.items()
        if count > 0
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


@router.get("/error-endpoints", response_model=list[EndpointAnalytics])
def get_error_endpoint_analytics(
    db: Annotated[Session, Depends(get_db)],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
) -> list[EndpointAnalytics]:
    filters = [RequestLog.status_code >= 400, *_time_filters(start_time, end_time)]
    average_response_time = func.avg(RequestLog.response_time_ms)
    statement = (
        select(
            RequestLog.method,
            RequestLog.path,
            func.count().label("request_count"),
            func.count().label("error_count"),
            average_response_time.label("average_response_time_ms"),
        )
        .where(*filters)
        .group_by(RequestLog.method, RequestLog.path)
        .order_by(desc("error_count"), desc(average_response_time))
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


@router.get("/traffic", response_model=list[TrafficBucket])
def get_traffic_over_time(
    db: Annotated[Session, Depends(get_db)],
    interval: Annotated[str, Query(pattern="^(hour|day)$")] = "hour",
    start_time: datetime | None = None,
    end_time: datetime | None = None,
) -> list[TrafficBucket]:
    statement = (
        select(RequestLog)
        .where(*_time_filters(start_time, end_time))
        .order_by(RequestLog.created_at)
    )
    buckets: dict[str, TrafficBucket] = {}

    for log in db.scalars(statement):
        bucket = _format_traffic_bucket(log.created_at, interval)
        if bucket not in buckets:
            buckets[bucket] = TrafficBucket(bucket=bucket, request_count=0, error_count=0)
        buckets[bucket].request_count += 1
        if log.status_code >= 400:
            buckets[bucket].error_count += 1

    return list(buckets.values())


@router.get("/latency-percentiles", response_model=LatencyPercentiles)
def get_latency_percentiles(
    db: Annotated[Session, Depends(get_db)],
    start_time: datetime | None = None,
    end_time: datetime | None = None,
) -> LatencyPercentiles:
    statement = (
        select(RequestLog.response_time_ms)
        .where(*_time_filters(start_time, end_time))
        .order_by(RequestLog.response_time_ms)
    )
    values = [float(value) for value in db.scalars(statement)]

    return LatencyPercentiles(
        p50_ms=_percentile(values, 0.50),
        p90_ms=_percentile(values, 0.90),
        p95_ms=_percentile(values, 0.95),
        p99_ms=_percentile(values, 0.99),
    )


def _time_filters(start_time: datetime | None, end_time: datetime | None) -> list[object]:
    filters = []
    if start_time is not None:
        filters.append(RequestLog.created_at >= start_time)
    if end_time is not None:
        filters.append(RequestLog.created_at <= end_time)
    return filters


def _format_traffic_bucket(created_at: datetime, interval: str) -> str:
    if interval == "day":
        return created_at.strftime("%Y-%m-%d")
    return created_at.strftime("%Y-%m-%dT%H:00:00")


def _percentile(values: list[float], percentile: float) -> float:
    if not values:
        return 0.0
    index = max(ceil(len(values) * percentile) - 1, 0)
    return round(values[index], 2)
