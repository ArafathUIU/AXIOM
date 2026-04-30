from fastapi import FastAPI

from app.api.analytics import router as analytics_router
from app.api.health import router as health_router
from app.api.logs import router as logs_router
from app.api.root import router as root_router
from app.core.config import settings
from app.db.init_db import init_db
from app.middleware.request_logger import register_request_logger
from app.models import RequestLog  # noqa: F401


def create_app() -> FastAPI:
    init_db()
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
    )
    register_request_logger(app)
    app.include_router(root_router)
    app.include_router(health_router)
    app.include_router(logs_router)
    app.include_router(analytics_router)
    return app


app = create_app()
