from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field


class CobrancaCreate(BaseModel):
    fatura_id: str = Field(pattern=r"^fat_[a-zA-Z0-9_-]+$")
    cliente_id: str = Field(pattern=r"^cli_[a-zA-Z0-9_-]+$")
    tipo: Literal["lembrete", "cobranca", "follow_up", "escalacao"]
    canal: Literal["whatsapp", "email", "sms"] = "whatsapp"
    mensagem: str | None = Field(default=None, max_length=2000)
    tom: Literal["amigavel", "neutro", "firme", "urgente"] | None = None


class CobrancaResponse(BaseModel):
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
