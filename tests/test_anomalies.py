from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_anomaly_preview_returns_empty_list_before_detectors() -> None:
    response = client.get("/anomalies/preview")

    assert response.status_code == 200
    assert response.json() == []
