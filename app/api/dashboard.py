from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter(tags=["dashboard"])

_DASHBOARD_FILE = Path(__file__).resolve().parents[1] / "static" / "dashboard.html"


@router.get("/dashboard", include_in_schema=False)
def dashboard() -> FileResponse:
    return FileResponse(_DASHBOARD_FILE)
