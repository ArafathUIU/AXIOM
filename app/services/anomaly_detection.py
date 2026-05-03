from datetime import UTC, datetime

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.core.config import settings
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

    return [*_detect_slow_response(db, filters)]


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
