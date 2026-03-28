"""Model de Webhook para notificacoes de eventos."""

from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Webhook(Base, TimestampMixin):
    """Webhook registrado para receber notificacoes de eventos."""

    __tablename__ = "webhooks"

    id: Mapped[str] = mapped_column(String(20), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(20), index=True)
    url: Mapped[str] = mapped_column(String(500))
    events: Mapped[str] = mapped_column(Text)  # JSON array as string
    active: Mapped[bool] = mapped_column(Boolean, default=True)
