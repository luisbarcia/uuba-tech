"""add authorization_url, token_url, scopes to oauth_apps

Revision ID: 012
Revises: 011

Migra URLs de OAuth de integration_providers para oauth_apps (1:N).
Copia dados existentes do provider para os apps associados.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "012"
down_revision = "011"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("oauth_apps", sa.Column("authorization_url", sa.Text, nullable=True))
    op.add_column("oauth_apps", sa.Column("token_url", sa.Text, nullable=True))
    op.add_column(
        "oauth_apps",
        sa.Column("scopes", postgresql.ARRAY(sa.Text), nullable=True),
    )

    # Copiar dados existentes de integration_providers para oauth_apps
    op.execute(
        """
        UPDATE oauth_apps oa
        SET
            authorization_url = ip.authorization_url,
            token_url = ip.token_url,
            scopes = CASE
                WHEN ip.default_scopes IS NOT NULL
                THEN string_to_array(ip.default_scopes, ip.scope_separator)
                ELSE NULL
            END
        FROM integration_providers ip
        WHERE oa.provider_id = ip.id
        """
    )


def downgrade() -> None:
    op.drop_column("oauth_apps", "scopes")
    op.drop_column("oauth_apps", "token_url")
    op.drop_column("oauth_apps", "authorization_url")
