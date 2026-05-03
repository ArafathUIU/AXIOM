from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.db.session import SessionLocal
from app.main import app
from app.models.ai_insight import AIInsight

client = TestClient(app)


def test_insights_can_be_generated_and_listed() -> None:
    with SessionLocal() as db:
        db.execute(delete(AIInsight))
        db.commit()

    create_response = client.post("/insights", json={"prompt": "What changed?"})

    assert create_response.status_code == 201
    assert create_response.json()["prompt"] == "What changed?"
    assert "AXIOM analyzed" in create_response.json()["summary"]

    list_response = client.get("/insights")

    assert list_response.status_code == 200
    assert list_response.json()["total"] == 1


def test_dashboard_summary_returns_combined_payload() -> None:
    response = client.get("/dashboard/summary")

    assert response.status_code == 200
    assert "analytics" in response.json()
    assert "latency" in response.json()
    assert "anomalies" in response.json()
