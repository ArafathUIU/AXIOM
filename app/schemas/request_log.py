from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RequestLogRead(BaseModel):
    id: int
    method: str
    path: str
    status_code: int
    response_time_ms: float
    client_ip: str | None
    user_agent: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RequestLogPage(BaseModel):
    items: list[RequestLogRead]
    total: int
    limit: int
    offset: int
