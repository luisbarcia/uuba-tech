"""add idempotency_cache table

Revision ID: 009
Revises: 008
"""

from alembic import op
import sqlalchemy as sa

revision = "009"
down_revision = "008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "idempotency_cache",
        sa.Column("key", sa.String(200), primary_key=True),
        sa.Column("body_hash", sa.String(64), nullable=False),
        sa.Column("response_status", sa.Integer(), nullable=False),
        sa.Column("response_body", sa.Text(), nullable=False),
        sa.Column(
            "response_content_type",
            sa.String(100),
            nullable=False,
            server_default="application/json",
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_idempotency_expires", "idempotency_cache", ["expires_at"])


def downgrade() -> None:
    op.drop_index("ix_idempotency_expires", table_name="idempotency_cache")
    op.drop_table("idempotency_cache")
