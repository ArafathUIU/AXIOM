from datetime import datetime

from pydantic import BaseModel, ConfigDict


class InsightCreate(BaseModel):
    prompt: str = "Summarize the current API health."


class InsightRead(BaseModel):
    id: int
    prompt: str
    summary: str
    model: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InsightPage(BaseModel):
    items: list[InsightRead]
    total: int
    limit: int
    offset: int
