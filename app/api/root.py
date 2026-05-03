from fastapi import APIRouter

router = APIRouter(tags=["root"])


@router.get("/")
def read_root() -> dict[str, str | dict[str, str]]:
    return {
        "name": "AXIOM",
        "description": "API Intelligence & Observability Monitor",
        "endpoints": {
            "health": "/health",
            "logs": "/logs?limit=20&offset=0",
            "recent_logs": "/logs/recent?limit=20",
            "analytics_summary": "/analytics/summary",
            "endpoint_analytics": "/analytics/endpoints",
            "slowest_endpoint_analytics": "/analytics/slowest-endpoints",
            "error_endpoint_analytics": "/analytics/error-endpoints",
            "traffic_analytics": "/analytics/traffic",
            "latency_percentiles": "/analytics/latency-percentiles",
            "status_code_analytics": "/analytics/status-codes",
            "status_code_family_analytics": "/analytics/status-code-families",
            "anomaly_preview": "/anomalies/preview",
            "docs": "/docs",
        },
    }
