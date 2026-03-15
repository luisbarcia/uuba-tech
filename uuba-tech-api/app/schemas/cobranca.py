from datetime import datetime
from typing import Literal
from pydantic import BaseModel


class CobrancaCreate(BaseModel):
    fatura_id: str
    cliente_id: str
    tipo: Literal["lembrete", "cobranca", "follow_up", "escalacao"]
    canal: Literal["whatsapp", "email", "sms"] = "whatsapp"
    mensagem: str | None = None
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
