from datetime import datetime

from pydantic import BaseModel, ConfigDict


class APIKeyRead(BaseModel):
    id: int
    name: str
    key_prefix: str
    is_active: bool
    request_count: int
    last_used_at: datetime | None
    revoked_at: datetime | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class APIKeyCreate(BaseModel):
    name: str


class APIKeyCreateResponse(APIKeyRead):
    key: str
