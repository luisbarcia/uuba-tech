"""Models para Régua de Cobrança.

A régua define a sequência de ações automáticas para faturas vencidas.
Cada passo especifica dias de atraso, tipo, canal, tom e template de mensagem.
"""

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Regua(Base, TimestampMixin):
    """Régua de cobrança — define a estratégia de cobrança automática."""

    __tablename__ = "reguas"

    id: Mapped[str] = mapped_column(String(20), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(20), index=True)
    nome: Mapped[str] = mapped_column(String(100))
    ativa: Mapped[bool] = mapped_column(Boolean, default=True)

    passos: Mapped[list["ReguaPasso"]] = relationship(
        back_populates="regua",
        lazy="selectin",
        order_by="ReguaPasso.dias_atraso",
    )


class ReguaPasso(Base, TimestampMixin):
    """Passo individual da régua — uma ação em D+N dias de atraso."""

    __tablename__ = "regua_passos"

    id: Mapped[str] = mapped_column(String(20), primary_key=True)
    regua_id: Mapped[str] = mapped_column(String(20), ForeignKey("reguas.id"))
    ordem: Mapped[int] = mapped_column(Integer)
    dias_atraso: Mapped[int] = mapped_column(Integer)
    tipo: Mapped[str] = mapped_column(String(30))  # lembrete, cobranca, follow_up, escalacao
    canal: Mapped[str] = mapped_column(String(20), default="whatsapp")
    tom: Mapped[str] = mapped_column(String(30))  # amigavel, neutro, firme, urgente
    template_mensagem: Mapped[str] = mapped_column(Text)

    regua: Mapped["Regua"] = relationship(back_populates="passos")
