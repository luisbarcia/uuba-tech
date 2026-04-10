"""drop tenants conta_azul legacy columns

Revision ID: 010
Revises: 009
"""

from alembic import op

revision = "010"
down_revision = "009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("tenants", "conta_azul_client_id")
    op.drop_column("tenants", "conta_azul_client_secret")
    op.drop_column("tenants", "conta_azul_access_token")
    op.drop_column("tenants", "conta_azul_refresh_token")


def downgrade() -> None:
    import sqlalchemy as sa

    op.add_column("tenants", sa.Column("conta_azul_refresh_token", sa.Text(), nullable=True))
    op.add_column("tenants", sa.Column("conta_azul_access_token", sa.Text(), nullable=True))
    op.add_column("tenants", sa.Column("conta_azul_client_secret", sa.Text(), nullable=True))
    op.add_column("tenants", sa.Column("conta_azul_client_id", sa.String(255), nullable=True))
