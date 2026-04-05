"""create webhooks table

Revision ID: 006
Revises: 005
"""
from alembic import op
import sqlalchemy as sa

revision = "006"
down_revision = "005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "webhooks",
        sa.Column("id", sa.String(20), primary_key=True),
        sa.Column("tenant_id", sa.String(20), nullable=False, index=True),
        sa.Column("url", sa.String(500), nullable=False),
        sa.Column("events", sa.Text, nullable=False),
        sa.Column("active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("webhooks")
