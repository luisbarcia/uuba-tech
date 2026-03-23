from datetime import datetime
from pydantic import BaseModel, Field

from app.domain.value_objects.fatura_status import FaturaStatus


class FaturaCreate(BaseModel):
    """Request body para criação de fatura (POST /api/v1/faturas). Valor em centavos."""

    cliente_id: str = Field(
        pattern=r"^cli_[a-zA-Z0-9_-]+$",
        description="ID do cliente (prefixo cli_)",
    )
    valor: int = Field(
        gt=0,
        description="Valor em centavos. R$ 25,00 = 2500",
    )
    vencimento: datetime = Field(
        description="Data de vencimento da fatura (ISO 8601)",
    )
    descricao: str | None = Field(
        default=None,
        max_length=500,
        description="Descrição livre da fatura, ex: serviço prestado",
    )
    numero_nf: str | None = Field(
        default=None,
        max_length=50,
        description="Número da nota fiscal vinculada",
    )


class FaturaUpdate(BaseModel):
    """Request body para atualização parcial de fatura (PATCH). Transições de status validadas via FaturaStatus."""

    status: FaturaStatus | None = Field(
        default=None,
        description="Status atual: pendente, pago, vencido ou cancelado",
    )
    promessa_pagamento: datetime | None = Field(
        default=None,
        description="Data em que o cliente prometeu pagar (ISO 8601)",
    )
    pagamento_link: str | None = Field(
        default=None,
        description="URL do link de pagamento (boleto, Pix, etc.)",
    )


class FaturaResponse(BaseModel):
    """Response body para fatura serializada da API."""

    id: str
    object: str = "fatura"
    cliente_id: str
    valor: int
    moeda: str
    status: str
    vencimento: datetime
    descricao: str | None = None
    numero_nf: str | None = None
    pagamento_link: str | None = None
    pago_em: datetime | None = None
    promessa_pagamento: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
