from pydantic import BaseModel

from app.schemas.analytics import AnalyticsSummary, EndpointAnalytics, LatencyPercentiles, TrafficBucket
from app.schemas.anomaly import AnomalySummary


class DashboardSummary(BaseModel):
    analytics: AnalyticsSummary
    latency: LatencyPercentiles
    traffic: list[TrafficBucket]
    endpoints: list[EndpointAnalytics]
    anomalies: AnomalySummary
