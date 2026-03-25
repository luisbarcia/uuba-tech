"""Modelo SQLAlchemy da fatura (tabela ``faturas``). Valor armazenado em centavos."""

from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin


class Fatura(Base, TimestampMixin):
    """Fatura vinculada a um cliente. Valor em centavos, status segue máquina de estados."""

    __tablename__ = "faturas"

    id: Mapped[str] = mapped_column(String(20), primary_key=True)  # fat_abc123
    tenant_id: Mapped[str] = mapped_column(String(20), index=True)
    cliente_id: Mapped[str] = mapped_column(String(20), ForeignKey("clientes.id"))
    valor: Mapped[int] = mapped_column(Integer)  # centavos
    moeda: Mapped[str] = mapped_column(String(3), default="BRL")
    status: Mapped[str] = mapped_column(String(20), default="pendente")
    # pendente | pago | vencido | cancelado
    vencimento: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    descricao: Mapped[str | None] = mapped_column(String(500), nullable=True)
    numero_nf: Mapped[str | None] = mapped_column(String(50), nullable=True)
    pagamento_link: Mapped[str | None] = mapped_column(String(500), nullable=True)
    pago_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    promessa_pagamento: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    cliente: Mapped["Cliente"] = relationship(back_populates="faturas", lazy="raise")

    __table_args__ = (
        Index("ix_faturas_status", "status"),
        Index("ix_faturas_vencimento", "vencimento"),
        Index("ix_faturas_cliente_id", "cliente_id"),
    )
