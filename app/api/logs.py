from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.request_log import RequestLog
from app.schemas.request_log import RequestLogPage, RequestLogRead

router = APIRouter(prefix="/logs", tags=["logs"])


@router.get("", response_model=RequestLogPage)
def list_logs(
    db: Annotated[Session, Depends(get_db)],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
    method: Annotated[str | None, Query(min_length=1, max_length=16)] = None,
    status_code: Annotated[int | None, Query(ge=100, le=599)] = None,
    path: Annotated[str | None, Query(min_length=1, max_length=512)] = None,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
) -> RequestLogPage:
    filters = []
    if method is not None:
        filters.append(RequestLog.method == method.upper())
    if status_code is not None:
        filters.append(RequestLog.status_code == status_code)
    if path is not None:
        filters.append(RequestLog.path.contains(path))
    if start_time is not None:
        filters.append(RequestLog.created_at >= start_time)
    if end_time is not None:
        filters.append(RequestLog.created_at <= end_time)

    total_statement = select(func.count()).select_from(RequestLog).where(*filters)
    total = db.scalar(total_statement) or 0
    statement = (
        select(RequestLog)
        .where(*filters)
        .order_by(desc(RequestLog.created_at))
        .offset(offset)
        .limit(limit)
    )
    items = list(db.scalars(statement).all())
    return RequestLogPage(items=items, total=total, limit=limit, offset=offset)


@router.get("/recent", response_model=list[RequestLogRead])
def get_recent_logs(
    db: Annotated[Session, Depends(get_db)],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> list[RequestLog]:
    statement = select(RequestLog).order_by(desc(RequestLog.created_at)).limit(limit)
    return list(db.scalars(statement).all())
