from sqlalchemy import String, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin


class Cliente(Base, TimestampMixin):
    __tablename__ = "clientes"

    id: Mapped[str] = mapped_column(String(20), primary_key=True)  # cli_abc123
    nome: Mapped[str] = mapped_column(String(255))
    documento: Mapped[str] = mapped_column(String(14))  # CPF ou CNPJ
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    telefone: Mapped[str | None] = mapped_column(String(20), nullable=True)  # 5521999990000

    faturas: Mapped[list["Fatura"]] = relationship(back_populates="cliente", lazy="raise")

    __table_args__ = (
        Index("ix_clientes_telefone", "telefone"),
        Index("ix_clientes_documento", "documento", unique=True),
    )
