from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field


class CobrancaCreate(BaseModel):
    """Request body para registrar uma cobrança (POST /api/v1/cobrancas)."""

    fatura_id: str = Field(
        pattern=r"^fat_[a-zA-Z0-9_-]+$",
        description="ID da fatura sendo cobrada (prefixo fat_)",
    )
    cliente_id: str = Field(
        pattern=r"^cli_[a-zA-Z0-9_-]+$",
        description="ID do cliente devedor (prefixo cli_)",
    )
    tipo: Literal["lembrete", "cobranca", "follow_up", "escalacao"] = Field(
        description="Tipo da ação: lembrete, cobranca, follow_up ou escalacao",
    )
    canal: Literal["whatsapp", "email", "sms"] = Field(
        default="whatsapp",
        description="Canal de envio: whatsapp, email ou sms",
    )
    mensagem: str | None = Field(
        default=None,
        max_length=2000,
        description="Texto da mensagem a ser enviada ao cliente",
    )
    tom: Literal["amigavel", "neutro", "firme", "urgente"] | None = Field(
        default=None,
        description="Tom da mensagem: amigavel, neutro, firme ou urgente",
    )


class CobrancaResponse(BaseModel):
    """Response body para cobrança serializada da API."""

    id: str
    object: str = "cobranca"
    fatura_id: str
    cliente_id: str
    tipo: str
    canal: str
    mensagem: str | None = None
    tom: str | None = None
    status: str
    pausado: bool
    agent_decision_id: str | None = None
    enviado_em: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
