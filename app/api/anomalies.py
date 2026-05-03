from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.anomaly import Anomaly
from app.schemas.anomaly import AnomalyPage, AnomalyRead, PersistedAnomalyRead
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
    start_time: datetime | None = None,
    end_time: datetime | None = None,
) -> list[Anomaly]:
    return persist_detected_anomalies(db, start_time=start_time, end_time=end_time)
