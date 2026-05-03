from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_dashboard_page_is_served() -> None:
    response = client.get("/dashboard")

    assert response.status_code == 200
    assert "AXIOM Dashboard" in response.text
