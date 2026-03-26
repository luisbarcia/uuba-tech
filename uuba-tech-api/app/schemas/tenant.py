"""Schemas Pydantic para Tenant — request/response bodies."""

from datetime import datetime

from pydantic import BaseModel, Field


class TenantCreate(BaseModel):
    """Request body para criacao de tenant (POST /api/v1/tenants)."""

    name: str = Field(
        min_length=1,
        max_length=255,
        description="Nome do tenant",
    )


class TenantUpdate(BaseModel):
    """Request body para atualizacao parcial de tenant (PATCH)."""

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="Novo nome do tenant",
    )
    active: bool | None = Field(
        default=None,
        description="Ativar/desativar tenant",
    )
    plan: str | None = Field(
        default=None,
        pattern=r"^(starter|pro|enterprise)$",
        description="Plano: starter, pro ou enterprise",
    )


class TenantResponse(BaseModel):
    """Response body para tenant serializado da API."""

    id: str
    object: str = "tenant"
    name: str
    slug: str
    active: bool
    plan: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_model(cls, tenant) -> "TenantResponse":
        """Converte modelo SQLAlchemy para response, mapeando campos."""
        return cls(
            id=tenant.id,
            name=tenant.nome,
            slug=tenant.slug,
            active=tenant.ativo,
            plan=tenant.plan,
            created_at=tenant.created_at,
            updated_at=tenant.updated_at,
        )
