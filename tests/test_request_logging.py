from datetime import timedelta

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


def test_logs_endpoint_returns_pagination_metadata() -> None:
    client.get("/first-paginated-log")
    client.get("/second-paginated-log")

    response = client.get("/logs?limit=1&offset=1")

    assert response.status_code == 200
    assert response.json()["total"] == 2
    assert response.json()["limit"] == 1
    assert response.json()["offset"] == 1
    assert len(response.json()["items"]) == 1


def test_logs_endpoint_filters_request_logs() -> None:
    client.get("/filter-me")
    client.post("/skip-me")

    response = client.get("/logs?method=get&status_code=404&path=filter")

    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["items"][0]["method"] == "GET"
    assert response.json()["items"][0]["path"] == "/filter-me"


def test_logs_endpoint_filters_by_time_range() -> None:
    client.get("/time-filtered-log")

    with SessionLocal() as db:
        log = db.scalar(select(RequestLog).where(RequestLog.path == "/time-filtered-log"))

    assert log is not None

    start_time = (log.created_at - timedelta(seconds=1)).isoformat()
    end_time = (log.created_at + timedelta(seconds=1)).isoformat()
    response = client.get(f"/logs?start_time={start_time}&end_time={end_time}")

    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["items"][0]["path"] == "/time-filtered-log"


def test_log_detail_endpoint_returns_request_log() -> None:
    client.get("/detail-log")

    with SessionLocal() as db:
        log = db.scalar(select(RequestLog).where(RequestLog.path == "/detail-log"))

    assert log is not None

    response = client.get(f"/logs/{log.id}")

    assert response.status_code == 200
    assert response.json()["id"] == log.id
    assert response.json()["path"] == "/detail-log"


def test_log_detail_endpoint_returns_404_for_missing_log() -> None:
    response = client.get("/logs/999999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Request log not found"}


def _clear_logs() -> None:
    with SessionLocal() as db:
        db.execute(delete(RequestLog))
        db.commit()


def _log_count() -> int:
    with SessionLocal() as db:
        return db.scalar(select(func.count()).select_from(RequestLog)) or 0
