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
            "docs": "/docs",
        },
    }
