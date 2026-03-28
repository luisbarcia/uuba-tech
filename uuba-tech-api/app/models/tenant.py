"""Model do Tenant (credor/empresa cliente da UUBA).

Cada tenant tem suas proprias credenciais, clientes, faturas e reguas.
Multi-tenancy via row-level filtering (tenant_id em todas as tabelas).

Com a migracao para Unkey, o campo ``api_key`` eh opcional (legacy).
API keys sao gerenciadas pelo Unkey, nao pela DB local.
"""

from sqlalchemy import Boolean, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


def _slugify(text: str) -> str:
    """Converte texto para slug URL-safe. Ex: 'Recbird Tech' -> 'recbird-tech'."""
    import re
    import unicodedata

    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[-\s]+", "-", text)
    return text.strip("-")


class Tenant(Base, TimestampMixin):
    """Empresa cliente da UUBA — o credor que usa a plataforma."""

    __tablename__ = "tenants"

    id: Mapped[str] = mapped_column(String(20), primary_key=True)  # ten_abc123
    nome: Mapped[str] = mapped_column(String(255))
    slug: Mapped[str] = mapped_column(String(255), default="")
    documento: Mapped[str | None] = mapped_column(String(14), nullable=True)  # CNPJ do credor
    api_key: Mapped[str | None] = mapped_column(String(100), nullable=True)  # legacy (Unkey)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    plan: Mapped[str] = mapped_column(String(20), default="starter")
    # starter | pro | enterprise

    # Conta Azul OAuth (para #17 — link de pagamento)
    conta_azul_client_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    conta_azul_client_secret: Mapped[str | None] = mapped_column(Text, nullable=True)
    conta_azul_access_token: Mapped[str | None] = mapped_column(Text, nullable=True)
    conta_azul_refresh_token: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (Index("ix_tenants_slug", "slug", unique=True),)
