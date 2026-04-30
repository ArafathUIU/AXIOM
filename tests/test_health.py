from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_root_returns_project_info() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["name"] == "AXIOM"
    assert response.json()["endpoints"]["health"] == "/health"


def test_health_check_returns_ok() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
