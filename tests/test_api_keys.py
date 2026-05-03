from app.models.api_key import APIKey


def test_api_key_model_defines_tracking_fields() -> None:
    assert APIKey.__tablename__ == "api_keys"
    assert hasattr(APIKey, "key_hash")
    assert hasattr(APIKey, "request_count")
    assert hasattr(APIKey, "revoked_at")
