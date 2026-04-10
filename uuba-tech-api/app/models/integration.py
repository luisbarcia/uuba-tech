"""Models do modulo de integracoes (cofre central).

4 tabelas criadas pela migration 002_integrations.sql no uuba-ctl:
- integration_providers: catalogo declarativo de providers
- tenant_integrations: instancia de integracao por tenant
- integration_credentials: credenciais encriptadas (AES-256-GCM)
- integration_events: historico imutavel de eventos
"""

from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    LargeBinary,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class IntegrationProvider(Base):
    """Catalogo declarativo de providers. Gerenciado por migration, nao editavel via API."""

    __tablename__ = "integration_providers"

    id: Mapped[str] = mapped_column(String(20), primary_key=True)  # plat_conta_azul
    slug: Mapped[str] = mapped_column(String(100), unique=True)
    name: Mapped[str] = mapped_column(String(200))
    category: Mapped[str] = mapped_column(String(50))  # erp, crm, payment, fiscal, banking
    base_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    token_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    authorization_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    default_scopes: Mapped[str | None] = mapped_column(Text, nullable=True)
    scope_separator: Mapped[str] = mapped_column(String(5), default=" ")
    connection_config_schema: Mapped[dict] = mapped_column(JSON, default=dict)
    credential_schema: Mapped[dict] = mapped_column(JSON, default=dict)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class TenantIntegration(Base, TimestampMixin):
    """Instancia de integracao por tenant. Cada tenant pode ter N integracoes por provider."""

    __tablename__ = "tenant_integrations"

    id: Mapped[str] = mapped_column(String(20), primary_key=True)  # tint_abc123
    tenant_id: Mapped[str] = mapped_column(String(20), ForeignKey("tenants.id"), index=True)
    provider_id: Mapped[str] = mapped_column(String(20), ForeignKey("integration_providers.id"))
    display_name: Mapped[str] = mapped_column(String(200))
    status: Mapped[str] = mapped_column(String(30), default="pending_setup")
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    connection_config: Mapped[dict] = mapped_column(JSON, default=dict)
    metadata_: Mapped[dict] = mapped_column("metadata", JSON, default=dict)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_count: Mapped[int] = mapped_column(Integer, default=0)
    oauth_app_id: Mapped[str | None] = mapped_column(
        String(25), ForeignKey("oauth_apps.id"), nullable=True
    )
    last_sync_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_error_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index(
            "uq_tenant_provider_display",
            "tenant_id",
            "provider_id",
            "display_name",
            unique=True,
        ),
    )


class IntegrationCredential(Base, TimestampMixin):
    """Credenciais encriptadas com AES-256-GCM. Uma por integracao (1:1)."""

    __tablename__ = "integration_credentials"

    id: Mapped[str] = mapped_column(String(20), primary_key=True)
    integration_id: Mapped[str] = mapped_column(
        String(20),
        ForeignKey("tenant_integrations.id", ondelete="CASCADE"),
        unique=True,
    )
    encrypted_data: Mapped[bytes] = mapped_column(LargeBinary)
    iv: Mapped[bytes] = mapped_column(LargeBinary)
    token_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    refresh_token_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_refreshed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class IntegrationEvent(Base):
    """Evento imutavel de integracao (historico de lifecycle)."""

    __tablename__ = "integration_events"

    id: Mapped[str] = mapped_column(String(20), primary_key=True)
    integration_id: Mapped[str] = mapped_column(
        String(20), ForeignKey("tenant_integrations.id", ondelete="CASCADE")
    )
    event_type: Mapped[str] = mapped_column(String(30))
    details: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        Index(
            "idx_integration_events_integration",
            "integration_id",
            "created_at",
        ),
    )
