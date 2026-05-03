from datetime import UTC, datetime
from hashlib import sha256
from secrets import token_urlsafe

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.api_key import APIKey


def hash_api_key(key: str) -> str:
    return sha256(key.encode("utf-8")).hexdigest()


def create_api_key(db: Session, name: str) -> tuple[APIKey, str]:
    raw_key = f"axm_{token_urlsafe(32)}"
    api_key = APIKey(
        name=name,
        key_prefix=raw_key[:12],
        key_hash=hash_api_key(raw_key),
    )
    db.add(api_key)
    db.commit()
    db.refresh(api_key)
    return api_key, raw_key


def find_active_api_key(db: Session, raw_key: str) -> APIKey | None:
    return db.scalar(
        select(APIKey).where(APIKey.key_hash == hash_api_key(raw_key), APIKey.is_active.is_(True))
    )


def mark_api_key_used(db: Session, api_key: APIKey) -> None:
    api_key.request_count += 1
    api_key.last_used_at = datetime.now(UTC)
    db.commit()


def revoke_api_key(db: Session, api_key: APIKey) -> APIKey:
    api_key.is_active = False
    api_key.revoked_at = datetime.now(UTC)
    db.commit()
    db.refresh(api_key)
    return api_key
