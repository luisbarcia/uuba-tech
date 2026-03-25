"""Model do Tenant (credor/empresa cliente da UÚBA).

Cada tenant tem suas próprias credenciais, clientes, faturas e réguas.
Multi-tenancy via row-level filtering (tenant_id em todas as tabelas).
"""

from sqlalchemy import Boolean, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Tenant(Base, TimestampMixin):
    """Empresa cliente da UÚBA — o credor que usa a plataforma."""

    __tablename__ = "tenants"

    id: Mapped[str] = mapped_column(String(20), primary_key=True)  # ten_abc123
    nome: Mapped[str] = mapped_column(String(255))
    documento: Mapped[str] = mapped_column(String(14))  # CNPJ do credor
    api_key: Mapped[str] = mapped_column(String(100))
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)

    # Conta Azul OAuth (para #17 — link de pagamento)
    conta_azul_client_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    conta_azul_client_secret: Mapped[str | None] = mapped_column(Text, nullable=True)
    conta_azul_access_token: Mapped[str | None] = mapped_column(Text, nullable=True)
    conta_azul_refresh_token: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index("ix_tenants_api_key", "api_key", unique=True),
        Index("ix_tenants_documento", "documento", unique=True),
    )
