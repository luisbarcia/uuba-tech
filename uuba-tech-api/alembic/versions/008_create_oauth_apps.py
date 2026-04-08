"""create oauth_apps table

Revision ID: 008
Revises: 007
"""
from alembic import op
import sqlalchemy as sa

revision = "008"
down_revision = "007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. oauth_apps — multiplos OAuth apps por provider
    op.create_table(
        "oauth_apps",
        sa.Column("id", sa.String(25), primary_key=True),
        sa.Column(
            "provider_id",
            sa.String(20),
            sa.ForeignKey("integration_providers.id"),
            nullable=False,
        ),
        sa.Column("label", sa.String(200), nullable=False),
        sa.Column("client_id", sa.Text, nullable=False),
        sa.Column("client_secret_encrypted", sa.LargeBinary, nullable=False),
        sa.Column("client_secret_iv", sa.LargeBinary, nullable=False),
        sa.Column("is_default", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("metadata", sa.JSON, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index(
        "uq_oauth_apps_provider_label",
        "oauth_apps",
        ["provider_id", "label"],
        unique=True,
    )
    op.create_index(
        "idx_oauth_apps_default",
        "oauth_apps",
        ["provider_id"],
        unique=True,
        postgresql_where=sa.text("is_default = true"),
    )

    # 2. Add oauth_app_id to tenant_integrations
    op.add_column(
        "tenant_integrations",
        sa.Column(
            "oauth_app_id",
            sa.String(25),
            sa.ForeignKey("oauth_apps.id"),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column("tenant_integrations", "oauth_app_id")
    op.drop_table("oauth_apps")
