from pydantic import BaseModel


class AnalyticsSummary(BaseModel):
    total_requests: int
    error_count: int
    error_rate: float
    average_response_time_ms: float


class EndpointAnalytics(BaseModel):
    method: str
    path: str
    request_count: int
    error_count: int
    average_response_time_ms: float


class StatusCodeAnalytics(BaseModel):
    status_code: int
    count: int


class TrafficBucket(BaseModel):
    bucket: str
    request_count: int
    error_count: int


class StatusCodeFamilyAnalytics(BaseModel):
    family: str
    count: int


class LatencyPercentiles(BaseModel):
    p50_ms: float
    p90_ms: float
    p95_ms: float
    p99_ms: float
