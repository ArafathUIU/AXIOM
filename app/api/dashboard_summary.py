from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.analytics import get_analytics_summary, get_endpoint_analytics, get_latency_percentiles, get_traffic_over_time
from app.api.anomalies import get_anomaly_summary
from app.db.session import get_db
from app.schemas.dashboard import DashboardSummary

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def get_dashboard_summary(db: Annotated[Session, Depends(get_db)]) -> DashboardSummary:
    return DashboardSummary(
        analytics=get_analytics_summary(db),
        latency=get_latency_percentiles(db),
        traffic=get_traffic_over_time(db, interval="hour"),
        endpoints=get_endpoint_analytics(db, limit=8),
        anomalies=get_anomaly_summary(db),
    )
