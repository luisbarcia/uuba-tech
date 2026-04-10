"""Model para OAuth apps — multiplos apps por provider."""

from sqlalchemy import Boolean, ForeignKey, Index, JSON, LargeBinary, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class OAuthApp(Base, TimestampMixin):
    """OAuth app (client_id + secret) associado a um provider.

    Permite multiplos apps por provider (ex: sandbox vs producao).
    Apenas um pode ser ``is_default=True`` por provider (partial unique index).
    """

    __tablename__ = "oauth_apps"

    id: Mapped[str] = mapped_column(String(25), primary_key=True)
    provider_id: Mapped[str] = mapped_column(String(20), ForeignKey("integration_providers.id"))
    label: Mapped[str] = mapped_column(String(200))
    client_id: Mapped[str] = mapped_column(Text)
    client_secret_encrypted: Mapped[bytes] = mapped_column(LargeBinary)
    client_secret_iv: Mapped[bytes] = mapped_column(LargeBinary)
    authorization_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    token_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    scopes: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    metadata_: Mapped[dict] = mapped_column("metadata", JSON, default=dict)

    __table_args__ = (
        Index("uq_oauth_apps_provider_label", "provider_id", "label", unique=True),
        Index(
            "idx_oauth_apps_default",
            "provider_id",
            unique=True,
            postgresql_where=text("is_default = true"),
        ),
    )
