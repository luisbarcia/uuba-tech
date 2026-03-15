from datetime import datetime
from pydantic import BaseModel


class ClienteCreate(BaseModel):
    nome: str
    documento: str
    email: str | None = None
    telefone: str | None = None


class ClienteUpdate(BaseModel):
    nome: str | None = None
    email: str | None = None
    telefone: str | None = None


class ClienteMetricas(BaseModel):
    dso_dias: float = 0.0
    total_em_aberto: int = 0
    total_vencido: int = 0
    faturas_em_aberto: int = 0
    faturas_vencidas: int = 0


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
