from datetime import datetime

from sqlalchemy import DateTime, String, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Cliente(Base, TimestampMixin):
    """Cliente da plataforma. Identificado por documento (CPF/CNPJ) único.

    LGPD: campo ``deletado_em`` indica anonimização (Art. 18 VI).
    Quando preenchido, PII foi substituído por valores neutros.
    """

    __tablename__ = "clientes"

    id: Mapped[str] = mapped_column(String(20), primary_key=True)  # cli_abc123
    nome: Mapped[str] = mapped_column(String(255))
    documento: Mapped[str] = mapped_column(String(14))  # CPF ou CNPJ
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    telefone: Mapped[str | None] = mapped_column(String(20), nullable=True)  # 5521999990000
    deletado_em: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )

    faturas: Mapped[list["Fatura"]] = relationship(back_populates="cliente", lazy="raise")

    __table_args__ = (
        Index("ix_clientes_telefone", "telefone"),
        Index("ix_clientes_documento", "documento", unique=True),
    )
