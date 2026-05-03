from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.api_keys import router as api_keys_router
from app.api.anomalies import router as anomalies_router
from app.api.analytics import router as analytics_router
from app.api.dashboard import router as dashboard_router
from app.api.dashboard_summary import router as dashboard_summary_router
from app.api.health import router as health_router
from app.api.insights import router as insights_router
from app.api.logs import router as logs_router
from app.api.root import router as root_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging
from app.db.init_db import init_db
from app.middleware.api_access import register_api_access_middleware
from app.middleware.request_logger import register_request_logger
from app.models import AIInsight, APIKey, Anomaly, RequestLog  # noqa: F401


def create_app() -> FastAPI:
    configure_logging()
    init_db()
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.mount("/assets", StaticFiles(directory="app/static"), name="assets")
    register_exception_handlers(app)
    register_api_access_middleware(app)
    register_request_logger(app)
    app.include_router(root_router)
    app.include_router(dashboard_router)
    app.include_router(health_router)
    app.include_router(logs_router)
    app.include_router(analytics_router)
    app.include_router(anomalies_router)
    app.include_router(api_keys_router)
    app.include_router(insights_router)
    app.include_router(dashboard_summary_router)
    return app


app = create_app()
