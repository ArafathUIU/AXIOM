import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, select

from app.db.session import SessionLocal
from app.main import app
from app.models.request_log import RequestLog

client = TestClient(app)


@pytest.fixture(autouse=True)
def seed_request_logs() -> None:
    _clear_logs()
    with SessionLocal() as db:
        db.add_all(
            [
                RequestLog(
                    method="GET",
                    path="/api/users",
                    status_code=200,
                    response_time_ms=10,
                    client_ip="127.0.0.1",
                    user_agent="test-client",
                ),
                RequestLog(
                    method="GET",
                    path="/api/users",
                    status_code=500,
                    response_time_ms=30,
                    client_ip="127.0.0.1",
                    user_agent="test-client",
                ),
                RequestLog(
                    method="POST",
                    path="/api/orders",
                    status_code=201,
                    response_time_ms=20,
                    client_ip="127.0.0.1",
                    user_agent="test-client",
                ),
                RequestLog(
                    method="GET",
                    path="/api/missing",
                    status_code=404,
                    response_time_ms=40,
                    client_ip="127.0.0.1",
                    user_agent="test-client",
                ),
            ]
        )
        db.commit()
    yield
    _clear_logs()


def test_analytics_summary_returns_core_metrics() -> None:
    response = client.get("/analytics/summary")

    assert response.status_code == 200
    assert response.json() == {
        "total_requests": 4,
        "error_count": 2,
        "error_rate": 50.0,
        "average_response_time_ms": 25.0,
    }


def test_endpoint_analytics_groups_by_method_and_path() -> None:
    response = client.get("/analytics/endpoints")

    assert response.status_code == 200
    assert response.json()[0] == {
        "method": "GET",
        "path": "/api/users",
        "request_count": 2,
        "error_count": 1,
        "average_response_time_ms": 20.0,
    }


def test_status_code_analytics_groups_by_status_code() -> None:
    response = client.get("/analytics/status-codes")

    assert response.status_code == 200
    assert response.json() == [
        {"status_code": 200, "count": 1},
        {"status_code": 201, "count": 1},
        {"status_code": 404, "count": 1},
        {"status_code": 500, "count": 1},
    ]


def test_analytics_summary_supports_time_window() -> None:
    with SessionLocal() as db:
        log = db.scalar(select(RequestLog).where(RequestLog.path == "/api/users"))

    assert log is not None

    timestamp = log.created_at.isoformat()
    response = client.get(f"/analytics/summary?start_time={timestamp}&end_time={timestamp}")

    assert response.status_code == 200
    assert response.json()["total_requests"] >= 1


def test_slowest_endpoint_analytics_orders_by_average_response_time() -> None:
    response = client.get("/analytics/slowest-endpoints")

    assert response.status_code == 200
    assert response.json()[0]["path"] == "/api/missing"
    assert response.json()[0]["average_response_time_ms"] == 40.0


def test_error_endpoint_analytics_returns_only_erroring_endpoints() -> None:
    response = client.get("/analytics/error-endpoints")

    assert response.status_code == 200
    assert response.json() == [
        {
            "method": "GET",
            "path": "/api/missing",
            "request_count": 1,
            "error_count": 1,
            "average_response_time_ms": 40.0,
        },
        {
            "method": "GET",
            "path": "/api/users",
            "request_count": 1,
            "error_count": 1,
            "average_response_time_ms": 30.0,
        },
    ]


def test_traffic_over_time_returns_request_and_error_counts() -> None:
    response = client.get("/analytics/traffic?interval=day")

    assert response.status_code == 200
    assert response.json() == [
        {
            "bucket": response.json()[0]["bucket"],
            "request_count": 4,
            "error_count": 2,
        }
    ]


def _clear_logs() -> None:
    with SessionLocal() as db:
        db.execute(delete(RequestLog))
        db.commit()
