"""Model para cache de idempotency — dedup de POST requests."""

from datetime import datetime, timezone

from sqlalchemy import String, Integer, Text, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class IdempotencyCache(Base):
    """Cache de idempotency para deduplicacao de POST requests.

    A chave e composta por ``{tenant_id}:{idempotency_key}`` com TTL de 24h.
    O ``body_hash`` (SHA-256) garante que o mesmo key com body diferente
    retorna 422 em vez de silenciosamente reutilizar a resposta cacheada.

    :param key: Chave composta ``{tenant_id}:{idempotency_key}`` (primary key).
    :param body_hash: SHA-256 do request body em hex (64 chars).
    :param response_status: HTTP status code da resposta original.
    :param response_body: Corpo da resposta original serializado como JSON string.
    :param response_content_type: Content-Type da resposta (default application/json).
    :param created_at: Timestamp de criacao em UTC.
    :param expires_at: Timestamp de expiracao em UTC (normalmente created_at + 24h).
    """

    __tablename__ = "idempotency_cache"

    key: Mapped[str] = mapped_column(String(200), primary_key=True)
    body_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    response_status: Mapped[int] = mapped_column(Integer, nullable=False)
    response_body: Mapped[str] = mapped_column(Text, nullable=False)
    response_content_type: Mapped[str] = mapped_column(
        String(100), nullable=False, server_default="application/json"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    __table_args__ = (
        Index("ix_idempotency_expires", "expires_at"),
    )
