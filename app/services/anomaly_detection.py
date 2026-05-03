from datetime import UTC, datetime

from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.anomaly import Anomaly
from app.models.request_log import RequestLog
from app.schemas.anomaly import AnomalyRead


def detect_anomalies(
    db: Session,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
) -> list[AnomalyRead]:
    filters = []
    if start_time is not None:
        filters.append(RequestLog.created_at >= start_time)
    if end_time is not None:
        filters.append(RequestLog.created_at <= end_time)

    return [
        *_detect_slow_response(db, filters),
        *_detect_error_spike(db, filters),
        *_detect_traffic_burst(db, filters),
    ]


def persist_detected_anomalies(
    db: Session,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
) -> list[Anomaly]:
    detected = detect_anomalies(db, start_time=start_time, end_time=end_time)
    anomalies = [
        Anomaly(
            type=anomaly.type,
            severity=anomaly.severity,
            message=anomaly.message,
            observed_value=anomaly.observed_value,
            threshold=anomaly.threshold,
            detected_at=anomaly.detected_at,
        )
        for anomaly in detected
    ]
    db.add_all(anomalies)
    db.commit()
    for anomaly in anomalies:
        db.refresh(anomaly)
    return anomalies


def _detect_slow_response(db: Session, filters: list[object]) -> list[AnomalyRead]:
    statement = (
        select(RequestLog)
        .where(RequestLog.response_time_ms >= settings.slow_response_threshold_ms)
        .where(*filters)
        .order_by(desc(RequestLog.response_time_ms))
        .limit(1)
    )
    slowest_log = db.scalar(statement)
    if slowest_log is None:
        return []

    return [
        AnomalyRead(
            type="slow_response",
            severity="warning",
            message=f"Slow response detected on {slowest_log.method} {slowest_log.path}",
            observed_value=round(float(slowest_log.response_time_ms), 2),
            threshold=settings.slow_response_threshold_ms,
            detected_at=datetime.now(UTC),
        )
    ]


def _detect_error_spike(db: Session, filters: list[object]) -> list[AnomalyRead]:
    total_requests = db.scalar(
        select(func.count()).select_from(RequestLog).where(*filters)
    ) or 0
    if total_requests == 0:
        return []

    error_count = db.scalar(
        select(func.count())
        .select_from(RequestLog)
        .where(RequestLog.status_code >= 400)
        .where(*filters)
    ) or 0
    error_rate = error_count / total_requests * 100
    if error_rate < settings.error_rate_threshold_percent:
        return []

    return [
        AnomalyRead(
            type="error_spike",
            severity="critical",
            message=f"Error rate reached {error_rate:.2f}% across {total_requests} requests",
            observed_value=round(error_rate, 2),
            threshold=settings.error_rate_threshold_percent,
            detected_at=datetime.now(UTC),
        )
    ]


def _detect_traffic_burst(db: Session, filters: list[object]) -> list[AnomalyRead]:
    total_requests = db.scalar(
        select(func.count()).select_from(RequestLog).where(*filters)
    ) or 0
    if total_requests < settings.traffic_burst_threshold_count:
        return []

    return [
        AnomalyRead(
            type="traffic_burst",
            severity="warning",
            message=f"Traffic volume reached {total_requests} requests",
            observed_value=float(total_requests),
            threshold=float(settings.traffic_burst_threshold_count),
            detected_at=datetime.now(UTC),
        )
    ]
