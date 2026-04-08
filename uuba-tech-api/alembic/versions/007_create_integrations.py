"""create integration tables + oauth_state_tokens

Revision ID: 007
Revises: 006
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "007"
down_revision = "006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. integration_providers — catalogo declarativo de providers
    op.create_table(
        "integration_providers",
        sa.Column("id", sa.String(20), primary_key=True),
        sa.Column("slug", sa.String(100), unique=True, nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("auth_type", sa.String(30), nullable=False),
        sa.Column("auth_types", postgresql.ARRAY(sa.Text), nullable=True),
        sa.Column("base_url", sa.Text, nullable=True),
        sa.Column("token_url", sa.Text, nullable=True),
        sa.Column("authorization_url", sa.Text, nullable=True),
        sa.Column("default_scopes", sa.Text, nullable=True),
        sa.Column("scope_separator", sa.String(5), server_default=" "),
        sa.Column("connection_config_schema", sa.JSON, server_default="{}"),
        sa.Column("credential_schema", sa.JSON, server_default="{}"),
        sa.Column("oauth_client_id", sa.Text, nullable=True),
        sa.Column("oauth_client_secret_encrypted", sa.LargeBinary, nullable=True),
        sa.Column("is_active", sa.Boolean, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # 2. tenant_integrations — instancia de integracao por tenant
    op.create_table(
        "tenant_integrations",
        sa.Column("id", sa.String(20), primary_key=True),
        sa.Column(
            "tenant_id",
            sa.String(20),
            sa.ForeignKey("tenants.id"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "provider_id",
            sa.String(20),
            sa.ForeignKey("integration_providers.id"),
            nullable=False,
        ),
        sa.Column("display_name", sa.String(200), nullable=False),
        sa.Column("status", sa.String(30), server_default="pending_setup"),
        sa.Column("enabled", sa.Boolean, server_default=sa.text("true")),
        sa.Column("connection_config", sa.JSON, server_default="{}"),
        sa.Column("metadata", sa.JSON, server_default="{}"),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("error_count", sa.Integer, server_default="0"),
        sa.Column("last_sync_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_error_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index(
        "uq_tenant_provider_display",
        "tenant_integrations",
        ["tenant_id", "provider_id", "display_name"],
        unique=True,
    )

    # 3. integration_credentials — credenciais encriptadas (AES-256-GCM)
    op.create_table(
        "integration_credentials",
        sa.Column("id", sa.String(20), primary_key=True),
        sa.Column(
            "integration_id",
            sa.String(20),
            sa.ForeignKey("tenant_integrations.id", ondelete="CASCADE"),
            unique=True,
            nullable=False,
        ),
        sa.Column("encrypted_data", sa.LargeBinary, nullable=False),
        sa.Column("iv", sa.LargeBinary, nullable=False),
        sa.Column("token_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("refresh_token_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_refreshed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # 4. integration_events — historico imutavel
    op.create_table(
        "integration_events",
        sa.Column("id", sa.String(20), primary_key=True),
        sa.Column(
            "integration_id",
            sa.String(20),
            sa.ForeignKey("tenant_integrations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("event_type", sa.String(30), nullable=False),
        sa.Column("details", sa.JSON, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index(
        "idx_integration_events_integration",
        "integration_events",
        ["integration_id", "created_at"],
    )

    # 5. oauth_state_tokens — rastreamento de fluxos OAuth em andamento
    op.create_table(
        "oauth_state_tokens",
        sa.Column("id", sa.String(20), primary_key=True),
        sa.Column("state_token", sa.String(64), unique=True, nullable=False),
        sa.Column("integration_id", sa.String(20), nullable=False),
        sa.Column("provider_slug", sa.String(100), nullable=False),
        sa.Column("scopes", sa.Text, nullable=True),
        sa.Column("code_verifier", sa.String(128), nullable=True),
        sa.Column("redirect_uri", sa.Text, nullable=False),
        sa.Column("status", sa.String(20), server_default="pending"),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("idx_oauth_state_token", "oauth_state_tokens", ["state_token"])

    # Seed providers
    op.execute(
        """
        INSERT INTO integration_providers (id, slug, name, category, auth_type, auth_types, base_url, token_url, authorization_url, default_scopes, is_active, created_at)
        VALUES
            ('plat_conta_azul', 'conta-azul', 'Conta Azul', 'erp', 'OAUTH2', '{OAUTH2}', 'https://api-v2.contaazul.com/v1', 'https://auth.contaazul.com/oauth2/token', 'https://auth.contaazul.com/oauth2/authorize', 'openid profile', true, NOW()),
            ('plat_pipedrive', 'pipedrive', 'Pipedrive', 'crm', 'API_KEY', '{API_KEY}', 'https://api.pipedrive.com/v1', NULL, NULL, NULL, true, NOW())
        """
    )


def downgrade() -> None:
    op.drop_table("oauth_state_tokens")
    op.drop_table("integration_events")
    op.drop_table("integration_credentials")
    op.drop_table("tenant_integrations")
    op.drop_table("integration_providers")
