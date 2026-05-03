"""add ai insights table

Revision ID: 20260503_003
Revises: 20260503_002
Create Date: 2026-05-03 00:00:00
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260503_003"
down_revision: str | None = "20260503_002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "ai_insights",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("prompt", sa.String(length=512), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("model", sa.String(length=128), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_ai_insights_created_at"), "ai_insights", ["created_at"], unique=False)
    op.create_index(op.f("ix_ai_insights_id"), "ai_insights", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_ai_insights_id"), table_name="ai_insights")
    op.drop_index(op.f("ix_ai_insights_created_at"), table_name="ai_insights")
    op.drop_table("ai_insights")
