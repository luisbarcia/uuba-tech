from datetime import datetime
from pydantic import BaseModel, Field


class ClienteCreate(BaseModel):
    """Request body para criação de cliente (POST /api/v1/clientes)."""

    nome: str = Field(
        min_length=1,
        max_length=255,
        description="Nome completo ou razão social do cliente",
    )
    documento: str = Field(
        min_length=11,
        max_length=14,
        pattern=r"^\d{11,14}$",
        description="CPF (11 dígitos) ou CNPJ (14 dígitos), apenas números",
    )
    email: str | None = Field(
        default=None,
        max_length=255,
        description="E-mail de contato do cliente",
    )
    telefone: str | None = Field(
        default=None,
        max_length=20,
        description="Telefone com DDD, ex: 11999998888",
    )


class ClienteUpdate(BaseModel):
    """Request body para atualização parcial de cliente (PATCH)."""

    nome: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="Nome completo ou razão social do cliente",
    )
    email: str | None = Field(
        default=None,
        max_length=255,
        description="E-mail de contato do cliente",
    )
    telefone: str | None = Field(
        default=None,
        max_length=20,
        description="Telefone com DDD, ex: 11999998888",
    )


class ClienteMetricas(BaseModel):
    """Métricas financeiras de um cliente (DSO, aging, totais em aberto)."""

    dso_dias: float = Field(
        default=0.0,
        description="Days Sales Outstanding — média de dias que o cliente leva para pagar",
    )
    total_em_aberto: int = Field(
        default=0,
        description="Valor total em aberto em centavos",
    )
    total_vencido: int = Field(
        default=0,
        description="Valor total vencido em centavos",
    )
    faturas_em_aberto: int = Field(
        default=0,
        description="Quantidade de faturas pendentes (não vencidas)",
    )
    faturas_vencidas: int = Field(
        default=0,
        description="Quantidade de faturas vencidas e não pagas",
    )


class ClienteResponse(BaseModel):
    """Response body para cliente serializado da API."""

    id: str
    object: str = "cliente"
    nome: str
    documento: str
    email: str | None = None
    telefone: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ClienteListItem(BaseModel):
    """Response para listagens — documento mascarado (LGPD Art. 46)."""

    id: str
    object: str = "cliente"
    nome: str
    documento_mascarado: str
    email: str | None = None
    telefone: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_cliente(cls, c) -> "ClienteListItem":
        doc = c.documento
        if len(doc) == 11:
            masked = f"***.{doc[3:6]}.***-{doc[9:]}"
        elif len(doc) == 14:
            masked = f"**.{doc[2:5]}.{doc[5:8]}/****-{doc[12:]}"
        else:
            masked = "***"
        return cls(
            id=c.id,
            nome=c.nome,
            documento_mascarado=masked,
            email=c.email,
            telefone=c.telefone,
            created_at=c.created_at,
            updated_at=c.updated_at,
        )
