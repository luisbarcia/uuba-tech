"""Model de Audit Log (LGPD Art. 37).

Registra operações de tratamento de dados pessoais.
"""

from datetime import datetime, timezone

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class AuditLog(Base):
    """Registro de auditoria de acesso a dados pessoais."""

    __tablename__ = "audit_log"

    id: Mapped[str] = mapped_column(String(20), primary_key=True)
    acao: Mapped[str] = mapped_column(String(30))  # criar, ler, atualizar, deletar
    recurso: Mapped[str] = mapped_column(String(30))  # cliente, fatura, cobranca
    recurso_id: Mapped[str | None] = mapped_column(String(20), nullable=True)
    detalhes: Mapped[str | None] = mapped_column(Text, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
