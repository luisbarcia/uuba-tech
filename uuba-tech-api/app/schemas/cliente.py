from datetime import datetime
from pydantic import BaseModel, Field


class ClienteCreate(BaseModel):
    nome: str = Field(
        min_length=1, max_length=255,
        description="Nome completo ou razão social do cliente",
    )
    documento: str = Field(
        min_length=11, max_length=14, pattern=r"^\d{11,14}$",
        description="CPF (11 dígitos) ou CNPJ (14 dígitos), apenas números",
    )
    email: str | None = Field(
        default=None, max_length=255,
        description="E-mail de contato do cliente",
    )
    telefone: str | None = Field(
        default=None, max_length=20,
        description="Telefone com DDD, ex: 11999998888",
    )


class ClienteUpdate(BaseModel):
    nome: str | None = Field(
        default=None, min_length=1, max_length=255,
        description="Nome completo ou razão social do cliente",
    )
    email: str | None = Field(
        default=None, max_length=255,
        description="E-mail de contato do cliente",
    )
    telefone: str | None = Field(
        default=None, max_length=20,
        description="Telefone com DDD, ex: 11999998888",
    )


class ClienteMetricas(BaseModel):
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
    id: str
    object: str = "cliente"
    nome: str
    documento: str
    email: str | None = None
    telefone: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
