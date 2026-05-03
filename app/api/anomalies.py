from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import require_admin_token
from app.models.anomaly import Anomaly
from app.schemas.anomaly import (
    AnomalyCount,
    AnomalyPage,
    AnomalyRead,
    AnomalySummary,
    PersistedAnomalyRead,
)
from app.services.anomaly_detection import detect_anomalies, persist_detected_anomalies

router = APIRouter(prefix="/anomalies", tags=["anomalies"])


@router.get("", response_model=AnomalyPage)
def list_anomalies(
    db: Annotated[Session, Depends(get_db)],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> AnomalyPage:
    total = db.scalar(select(func.count()).select_from(Anomaly)) or 0
    statement = (
        select(Anomaly)
        .order_by(desc(Anomaly.detected_at))
        .offset(offset)
        .limit(limit)
    )
    items = list(db.scalars(statement).all())
    return AnomalyPage(items=items, total=total, limit=limit, offset=offset)


@router.get("/summary", response_model=AnomalySummary)
def get_anomaly_summary(db: Annotated[Session, Depends(get_db)]) -> AnomalySummary:
    total = db.scalar(select(func.count()).select_from(Anomaly)) or 0
    severity_rows = db.execute(
        select(Anomaly.severity, func.count().label("count"))
        .group_by(Anomaly.severity)
        .order_by(desc("count"))
    )
    type_rows = db.execute(
        select(Anomaly.type, func.count().label("count"))
        .group_by(Anomaly.type)
        .order_by(desc("count"))
    )
    return AnomalySummary(
        total=total,
        by_severity=[
            AnomalyCount(name=row.severity, count=row.count) for row in severity_rows
        ],
        by_type=[AnomalyCount(name=row.type, count=row.count) for row in type_rows],
    )


@router.get("/preview", response_model=list[AnomalyRead])
def preview_anomalies(
    db: Annotated[Session, Depends(get_db)],
    start_time: datetime | None = None,
    end_time: datetime | None = None,
) -> list[AnomalyRead]:
    return detect_anomalies(db, start_time=start_time, end_time=end_time)


@router.post("/detect", response_model=list[PersistedAnomalyRead])
def detect_and_persist_anomalies(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[None, Depends(require_admin_token)],
    start_time: datetime | None = None,
    end_time: datetime | None = None,
) -> list[Anomaly]:
    return persist_detected_anomalies(db, start_time=start_time, end_time=end_time)
