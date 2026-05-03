from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.api_key import APIKey
from app.schemas.api_key import APIKeyCreate, APIKeyCreateResponse, APIKeyPage, APIKeyRead
from app.services.api_keys import create_api_key, revoke_api_key

router = APIRouter(prefix="/api-keys", tags=["api keys"])


@router.get("", response_model=APIKeyPage)
def list_api_keys(
    db: Annotated[Session, Depends(get_db)],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> APIKeyPage:
    total = db.scalar(select(func.count()).select_from(APIKey)) or 0
    statement = select(APIKey).order_by(desc(APIKey.created_at)).offset(offset).limit(limit)
    return APIKeyPage(
        items=list(db.scalars(statement).all()),
        total=total,
        limit=limit,
        offset=offset,
    )


@router.post("", response_model=APIKeyCreateResponse, status_code=201)
def create_key(
    payload: APIKeyCreate,
    db: Annotated[Session, Depends(get_db)],
) -> APIKeyCreateResponse:
    api_key, raw_key = create_api_key(db, payload.name)
    return APIKeyCreateResponse(
        id=api_key.id,
        name=api_key.name,
        key_prefix=api_key.key_prefix,
        is_active=api_key.is_active,
        request_count=api_key.request_count,
        last_used_at=api_key.last_used_at,
        revoked_at=api_key.revoked_at,
        created_at=api_key.created_at,
        key=raw_key,
    )


@router.post("/{api_key_id}/revoke", response_model=APIKeyRead)
def revoke_key(api_key_id: int, db: Annotated[Session, Depends(get_db)]) -> APIKey:
    api_key = db.get(APIKey, api_key_id)
    if api_key is None:
        raise HTTPException(status_code=404, detail="API key not found")
    return revoke_api_key(db, api_key)


@router.get("/{api_key_id}/analytics", response_model=APIKeyRead)
def get_api_key_analytics(api_key_id: int, db: Annotated[Session, Depends(get_db)]) -> APIKey:
    api_key = db.get(APIKey, api_key_id)
    if api_key is None:
        raise HTTPException(status_code=404, detail="API key not found")
    return api_key
