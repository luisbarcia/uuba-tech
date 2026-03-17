from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Text, Boolean, Index
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, TimestampMixin


class Cobranca(Base, TimestampMixin):
    """Registro de cobrança enviada ao cliente. Pode ser pausada e retomada."""

    __tablename__ = "cobrancas"

    id: Mapped[str] = mapped_column(String(20), primary_key=True)  # cob_abc123
    fatura_id: Mapped[str] = mapped_column(String(20), ForeignKey("faturas.id"))
    cliente_id: Mapped[str] = mapped_column(String(20), ForeignKey("clientes.id"))
    tipo: Mapped[str] = mapped_column(String(30))
    # lembrete | cobranca | follow_up | escalacao
    canal: Mapped[str] = mapped_column(String(20), default="whatsapp")
    mensagem: Mapped[str | None] = mapped_column(Text, nullable=True)
    tom: Mapped[str | None] = mapped_column(String(30), nullable=True)
    # amigavel | neutro | firme | urgente
    status: Mapped[str] = mapped_column(String(20), default="enviado")
    # enviado | entregue | lido | respondido | pausado
    pausado: Mapped[bool] = mapped_column(Boolean, default=False)
    agent_decision_id: Mapped[str | None] = mapped_column(String(20), nullable=True)
    enviado_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("ix_cobrancas_fatura_id", "fatura_id"),
        Index("ix_cobrancas_cliente_id", "cliente_id"),
    )
