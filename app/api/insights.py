from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import require_admin_token
from app.models.ai_insight import AIInsight
from app.schemas.insight import InsightCreate, InsightPage, InsightRead
from app.services.insights import generate_insight

router = APIRouter(prefix="/insights", tags=["insights"])


@router.post("", response_model=InsightRead, status_code=201)
def create_insight(
    payload: InsightCreate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[None, Depends(require_admin_token)],
) -> AIInsight:
    return generate_insight(db, payload.prompt)


@router.get("", response_model=InsightPage)
def list_insights(
    db: Annotated[Session, Depends(get_db)],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> InsightPage:
    total = db.scalar(select(func.count()).select_from(AIInsight)) or 0
    statement = select(AIInsight).order_by(desc(AIInsight.created_at)).offset(offset).limit(limit)
    return InsightPage(items=list(db.scalars(statement).all()), total=total, limit=limit, offset=offset)
