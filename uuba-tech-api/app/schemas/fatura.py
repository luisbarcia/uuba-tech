from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field


class FaturaCreate(BaseModel):
    cliente_id: str = Field(pattern=r"^cli_[a-zA-Z0-9_-]+$")
    valor: int = Field(gt=0)  # centavos, deve ser positivo
    vencimento: datetime
    descricao: str | None = Field(default=None, max_length=500)
    numero_nf: str | None = Field(default=None, max_length=50)


class FaturaUpdate(BaseModel):
    status: Literal["pendente", "pago", "vencido", "cancelado"] | None = None
    promessa_pagamento: datetime | None = None
    pagamento_link: str | None = None


class FaturaResponse(BaseModel):
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
