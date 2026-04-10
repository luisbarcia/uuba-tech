"""drop integration_providers.auth_type (singular) — deprecated by auth_types[]

Revision ID: 011
Revises: 010
"""

from alembic import op
import sqlalchemy as sa

revision = "011"
down_revision = "010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("integration_providers", "auth_type")


def downgrade() -> None:
    op.add_column(
        "integration_providers",
        sa.Column("auth_type", sa.String(30), nullable=True),
    )
