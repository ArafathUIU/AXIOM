from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AnomalyRead(BaseModel):
    type: str
    severity: str
    message: str
    observed_value: float
    threshold: float
    detected_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PersistedAnomalyRead(AnomalyRead):
    id: int
    created_at: datetime


class AnomalyPage(BaseModel):
    items: list[PersistedAnomalyRead]
    total: int
    limit: int
    offset: int
