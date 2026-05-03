import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.db.session import SessionLocal
from app.main import app
from app.models.request_log import RequestLog

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_request_logs() -> None:
    _clear_logs()
    yield
    _clear_logs()


def test_anomaly_preview_returns_empty_list_without_matching_logs() -> None:
    response = client.get("/anomalies/preview")

    assert response.status_code == 200
    assert response.json() == []


def test_anomaly_preview_detects_slow_responses() -> None:
    with SessionLocal() as db:
        db.add(
            RequestLog(
                method="GET",
                path="/slow",
                status_code=200,
                response_time_ms=1500,
                client_ip="127.0.0.1",
                user_agent="test-client",
            )
        )
        db.commit()

    response = client.get("/anomalies/preview")

    assert response.status_code == 200
    assert response.json()[0]["type"] == "slow_response"
    assert response.json()[0]["observed_value"] == 1500.0


def _clear_logs() -> None:
    with SessionLocal() as db:
        db.execute(delete(RequestLog))
        db.commit()
