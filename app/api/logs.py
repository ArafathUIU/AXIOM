from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.request_log import RequestLog
from app.schemas.request_log import RequestLogRead

router = APIRouter(prefix="/logs", tags=["logs"])


@router.get("/recent", response_model=list[RequestLogRead])
def get_recent_logs(
    db: Annotated[Session, Depends(get_db)],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> list[RequestLog]:
    statement = select(RequestLog).order_by(desc(RequestLog.created_at)).limit(limit)
    return list(db.scalars(statement).all())
