import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.db.session import SessionLocal
from app.main import app
from app.models.api_key import APIKey

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_api_keys() -> None:
    with SessionLocal() as db:
        db.execute(delete(APIKey))
        db.commit()
    yield
    with SessionLocal() as db:
        db.execute(delete(APIKey))
        db.commit()


def test_api_key_model_defines_tracking_fields() -> None:
    assert APIKey.__tablename__ == "api_keys"
    assert hasattr(APIKey, "key_hash")
    assert hasattr(APIKey, "request_count")
    assert hasattr(APIKey, "revoked_at")


def test_api_key_can_be_created_listed_used_and_revoked() -> None:
    create_response = client.post("/api-keys", json={"name": "dashboard"})

    assert create_response.status_code == 201
    raw_key = create_response.json()["key"]
    api_key_id = create_response.json()["id"]
    assert raw_key.startswith("axm_")

    health_response = client.get("/", headers={"x-api-key": raw_key})
    assert health_response.status_code == 200

    analytics_response = client.get(f"/api-keys/{api_key_id}/analytics")
    assert analytics_response.status_code == 200
    assert analytics_response.json()["request_count"] == 1

    list_response = client.get("/api-keys")
    assert list_response.status_code == 200
    assert list_response.json()["total"] == 1

    revoke_response = client.post(f"/api-keys/{api_key_id}/revoke")
    assert revoke_response.status_code == 200
    assert revoke_response.json()["is_active"] is False

    rejected_response = client.get("/", headers={"x-api-key": raw_key})
    assert rejected_response.status_code == 401
