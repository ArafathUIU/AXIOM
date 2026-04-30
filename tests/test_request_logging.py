import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, func, select

from app.db.session import SessionLocal
from app.main import app
from app.models.request_log import RequestLog

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_request_logs() -> None:
    _clear_logs()
    yield
    _clear_logs()


def test_health_check_is_not_logged() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert _log_count() == 0


def test_request_is_logged() -> None:
    response = client.get("/missing-endpoint")

    assert response.status_code == 404

    with SessionLocal() as db:
        log = db.scalar(select(RequestLog))

    assert log is not None
    assert log.method == "GET"
    assert log.path == "/missing-endpoint"
    assert log.status_code == 404
    assert log.response_time_ms >= 0


def test_recent_logs_endpoint_returns_request_logs() -> None:
    client.get("/missing-for-recent-logs")

    response = client.get("/logs/recent?limit=1")

    assert response.status_code == 200
    assert response.json()[0]["path"] == "/missing-for-recent-logs"


def _clear_logs() -> None:
    with SessionLocal() as db:
        db.execute(delete(RequestLog))
        db.commit()


def _log_count() -> int:
    with SessionLocal() as db:
        return db.scalar(select(func.count()).select_from(RequestLog)) or 0
