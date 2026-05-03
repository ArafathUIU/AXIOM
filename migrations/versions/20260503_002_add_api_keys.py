"""add api keys table

Revision ID: 20260503_002
Revises: 20260503_001
Create Date: 2026-05-03 00:00:00
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260503_002"
down_revision: str | None = "20260503_001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "api_keys",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("key_prefix", sa.String(length=16), nullable=False),
        sa.Column("key_hash", sa.String(length=128), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("request_count", sa.Integer(), nullable=False),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_api_keys_created_at"), "api_keys", ["created_at"], unique=False)
    op.create_index(op.f("ix_api_keys_id"), "api_keys", ["id"], unique=False)
    op.create_index(op.f("ix_api_keys_is_active"), "api_keys", ["is_active"], unique=False)
    op.create_index(op.f("ix_api_keys_key_hash"), "api_keys", ["key_hash"], unique=True)
    op.create_index(op.f("ix_api_keys_key_prefix"), "api_keys", ["key_prefix"], unique=False)
    op.create_index(op.f("ix_api_keys_name"), "api_keys", ["name"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_api_keys_name"), table_name="api_keys")
    op.drop_index(op.f("ix_api_keys_key_prefix"), table_name="api_keys")
    op.drop_index(op.f("ix_api_keys_key_hash"), table_name="api_keys")
    op.drop_index(op.f("ix_api_keys_is_active"), table_name="api_keys")
    op.drop_index(op.f("ix_api_keys_id"), table_name="api_keys")
    op.drop_index(op.f("ix_api_keys_created_at"), table_name="api_keys")
    op.drop_table("api_keys")
