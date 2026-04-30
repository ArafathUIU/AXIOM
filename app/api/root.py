from fastapi import APIRouter

router = APIRouter(tags=["root"])


@router.get("/")
def read_root() -> dict[str, str | dict[str, str]]:
    return {
        "name": "AXIOM",
        "description": "API Intelligence & Observability Monitor",
        "endpoints": {
            "health": "/health",
            "recent_logs": "/logs/recent?limit=20",
            "analytics_summary": "/analytics/summary",
            "endpoint_analytics": "/analytics/endpoints",
            "status_code_analytics": "/analytics/status-codes",
            "docs": "/docs",
        },
    }
