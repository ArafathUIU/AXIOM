from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.db.session import SessionLocal
from app.main import app
from app.core.config import settings
from app.models.anomaly import Anomaly
from app.models.request_log import RequestLog

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_request_logs() -> None:
    _clear_data()
    yield
    _clear_data()


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


def test_anomaly_preview_detects_error_spikes() -> None:
    with SessionLocal() as db:
        db.add_all(
            [
                RequestLog(
                    method="GET",
                    path="/ok",
                    status_code=200,
                    response_time_ms=20,
                    client_ip="127.0.0.1",
                    user_agent="test-client",
                ),
                RequestLog(
                    method="GET",
                    path="/error-one",
                    status_code=500,
                    response_time_ms=30,
                    client_ip="127.0.0.1",
                    user_agent="test-client",
                ),
                RequestLog(
                    method="GET",
                    path="/error-two",
                    status_code=502,
                    response_time_ms=40,
                    client_ip="127.0.0.1",
                    user_agent="test-client",
                ),
            ]
        )
        db.commit()

    response = client.get("/anomalies/preview")

    assert response.status_code == 200
    assert response.json()[0]["type"] == "error_spike"
    assert response.json()[0]["observed_value"] == 66.67


def test_anomaly_preview_detects_traffic_bursts() -> None:
    with SessionLocal() as db:
        db.add_all(
            RequestLog(
                method="GET",
                path="/busy",
                status_code=200,
                response_time_ms=20,
                client_ip="127.0.0.1",
                user_agent="test-client",
            )
            for _ in range(100)
        )
        db.commit()

    response = client.get("/anomalies/preview")

    assert response.status_code == 200
    assert response.json()[0]["type"] == "traffic_burst"
    assert response.json()[0]["observed_value"] == 100.0


def test_anomaly_detection_persists_detected_anomalies() -> None:
    with SessionLocal() as db:
        db.add(
            RequestLog(
                method="GET",
                path="/persisted-slow",
                status_code=200,
                response_time_ms=1500,
                client_ip="127.0.0.1",
                user_agent="test-client",
            )
        )
        db.commit()

    response = client.post("/anomalies/detect")

    assert response.status_code == 200
    assert response.json()[0]["id"] is not None
    assert response.json()[0]["type"] == "slow_response"

    with SessionLocal() as db:
        persisted = db.get(Anomaly, response.json()[0]["id"])

    assert persisted is not None
    assert persisted.type == "slow_response"


def test_anomaly_listing_returns_persisted_anomalies() -> None:
    with SessionLocal() as db:
        db.add(
            Anomaly(
                type="slow_response",
                severity="warning",
                message="Slow response detected",
                observed_value=1500,
                threshold=1000,
                detected_at=datetime.now(UTC),
            )
        )
        db.commit()

    response = client.get("/anomalies?limit=1&offset=0")

    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["limit"] == 1
    assert response.json()["offset"] == 0
    assert response.json()["items"][0]["type"] == "slow_response"


def test_anomaly_summary_groups_persisted_anomalies() -> None:
    with SessionLocal() as db:
        db.add_all(
            [
                Anomaly(
                    type="slow_response",
                    severity="warning",
                    message="Slow response detected",
                    observed_value=1500,
                    threshold=1000,
                    detected_at=datetime.now(UTC),
                ),
                Anomaly(
                    type="error_spike",
                    severity="critical",
                    message="Error spike detected",
                    observed_value=75,
                    threshold=50,
                    detected_at=datetime.now(UTC),
                ),
            ]
        )
        db.commit()

    response = client.get("/anomalies/summary")

    assert response.status_code == 200
    assert response.json()["total"] == 2
    assert {item["name"]: item["count"] for item in response.json()["by_severity"]} == {
        "warning": 1,
        "critical": 1,
    }
    assert {item["name"]: item["count"] for item in response.json()["by_type"]} == {
        "slow_response": 1,
        "error_spike": 1,
    }


def test_anomaly_detection_requires_admin_token_when_configured() -> None:
    original_admin_token = settings.admin_token
    settings.admin_token = "test-admin-token"
    try:
        rejected_response = client.post("/anomalies/detect")
        accepted_response = client.post(
            "/anomalies/detect",
            headers={"X-Admin-Token": "test-admin-token"},
        )
    finally:
        settings.admin_token = original_admin_token

    assert rejected_response.status_code == 403
    assert accepted_response.status_code == 200


def _clear_data() -> None:
    with SessionLocal() as db:
        db.execute(delete(Anomaly))
        db.execute(delete(RequestLog))
        db.commit()
