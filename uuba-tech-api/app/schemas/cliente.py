from datetime import datetime
from pydantic import BaseModel, Field


class ClienteCreate(BaseModel):
    nome: str = Field(min_length=1, max_length=255)
    documento: str = Field(min_length=11, max_length=14, pattern=r"^\d{11,14}$")
    email: str | None = Field(default=None, max_length=255)
    telefone: str | None = Field(default=None, max_length=20)


class ClienteUpdate(BaseModel):
    nome: str | None = Field(default=None, min_length=1, max_length=255)
    email: str | None = Field(default=None, max_length=255)
    telefone: str | None = Field(default=None, max_length=20)


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
