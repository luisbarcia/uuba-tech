"""Model para OAuth state tokens — rastreamento de fluxos OAuth em andamento."""

import secrets
from datetime import datetime, timezone

from sqlalchemy import DateTime, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class OAuthStateToken(Base):
    """Token de estado para fluxo OAuth2 Authorization Code + PKCE."""

    __tablename__ = "oauth_state_tokens"

    id: Mapped[str] = mapped_column(String(20), primary_key=True)
    state_token: Mapped[str] = mapped_column(String(64), unique=True)
    integration_id: Mapped[str] = mapped_column(String(20))
    provider_slug: Mapped[str] = mapped_column(String(100))
    scopes: Mapped[str | None] = mapped_column(Text, nullable=True)
    code_verifier: Mapped[str | None] = mapped_column(String(128), nullable=True)
    redirect_uri: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending | completed | expired
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (
        Index("idx_oauth_state_token", "state_token"),
    )

    @staticmethod
    def generate_state() -> str:
        return secrets.token_hex(32)  # 64 chars
