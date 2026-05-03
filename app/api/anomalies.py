from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.anomaly import AnomalyRead
from app.services.anomaly_detection import detect_anomalies

router = APIRouter(prefix="/anomalies", tags=["anomalies"])


@router.get("/preview", response_model=list[AnomalyRead])
def preview_anomalies(
    db: Annotated[Session, Depends(get_db)],
    start_time: datetime | None = None,
    end_time: datetime | None = None,
) -> list[AnomalyRead]:
    return detect_anomalies(db, start_time=start_time, end_time=end_time)
