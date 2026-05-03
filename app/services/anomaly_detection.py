from datetime import datetime

from sqlalchemy.orm import Session

from app.schemas.anomaly import AnomalyRead


def detect_anomalies(
    db: Session,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
) -> list[AnomalyRead]:
    return []
