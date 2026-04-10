"""Model do Tenant (credor/empresa cliente da UUBA).

Cada tenant tem suas proprias credenciais, clientes, faturas e reguas.
Multi-tenancy via row-level filtering (tenant_id em todas as tabelas).
API keys sao gerenciadas pelo Unkey (nao pela DB local).
"""

from sqlalchemy import Boolean, Index, String
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
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    plan: Mapped[str] = mapped_column(String(20), default="starter")
    # starter | pro | enterprise

    __table_args__ = (Index("ix_tenants_slug", "slug", unique=True),)
