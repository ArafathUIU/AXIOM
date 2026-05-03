"""add anomalies table

Revision ID: 20260503_001
Revises: None
Create Date: 2026-05-03 00:00:00
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260503_001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "anomalies",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("type", sa.String(length=64), nullable=False),
        sa.Column("severity", sa.String(length=32), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("observed_value", sa.Float(), nullable=False),
        sa.Column("threshold", sa.Float(), nullable=False),
        sa.Column("detected_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_anomalies_created_at"), "anomalies", ["created_at"], unique=False)
    op.create_index(op.f("ix_anomalies_detected_at"), "anomalies", ["detected_at"], unique=False)
    op.create_index(op.f("ix_anomalies_id"), "anomalies", ["id"], unique=False)
    op.create_index(op.f("ix_anomalies_severity"), "anomalies", ["severity"], unique=False)
    op.create_index(op.f("ix_anomalies_type"), "anomalies", ["type"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_anomalies_type"), table_name="anomalies")
    op.drop_index(op.f("ix_anomalies_severity"), table_name="anomalies")
    op.drop_index(op.f("ix_anomalies_id"), table_name="anomalies")
    op.drop_index(op.f("ix_anomalies_detected_at"), table_name="anomalies")
    op.drop_index(op.f("ix_anomalies_created_at"), table_name="anomalies")
    op.drop_table("anomalies")
