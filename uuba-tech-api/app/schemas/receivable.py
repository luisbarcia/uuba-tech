"""Schemas do endpoint POST /api/v1/receivables — Canonical Data Model.

Compativel com o payload da CFO Automation API (cfo-api).
Permite migracao transparente: cliente muda URL + API key, payload identico.

Fonte: openapi/components/schemas/canonical.yaml do repo cfo-automation-api.
"""

from datetime import date
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


# --- Enums ---


class PersonType(str, Enum):
    PF = "PF"
    PJ = "PJ"


class Frequency(str, Enum):
    MENSAL = "MENSAL"
    ANUAL = "ANUAL"


class BrazilianState(str, Enum):
    AC = "AC"
    AL = "AL"
    AP = "AP"
    AM = "AM"
    BA = "BA"
    CE = "CE"
    DF = "DF"
    ES = "ES"
    GO = "GO"
    MA = "MA"
    MT = "MT"
    MS = "MS"
    MG = "MG"
    PA = "PA"
    PB = "PB"
    PR = "PR"
    PE = "PE"
    PI = "PI"
    RJ = "RJ"
    RN = "RN"
    RS = "RS"
    RO = "RO"
    RR = "RR"
    SC = "SC"
    SE = "SE"
    SP = "SP"
    TO = "TO"


class ReceivableStatus(str, Enum):
    COMPLETED = "completed"
    PARTIAL = "partial"
    FAILED = "failed"


class OperationStatus(str, Enum):
    CREATED = "created"
    FAILED = "failed"


# --- Sub-schemas ---


class Contact(BaseModel):
    """Contato associado a um cliente PJ."""

    name: str = Field(..., max_length=200)
    email: str | None = None
    phone: str | None = None
    mobile: str | None = None
    role: str | None = Field(None, max_length=100)

    model_config = {"extra": "forbid"}


class Address(BaseModel):
    """Endereco do cliente."""

    street: str | None = Field(None, max_length=200)
    number: str | None = Field(None, max_length=20)
    complement: str | None = Field(None, max_length=100)
    neighborhood: str | None = Field(None, max_length=100)
    zip_code: str | None = None
    city: str | None = Field(None, max_length=100)
    state: BrazilianState | None = None

    model_config = {"extra": "forbid"}


class Customer(BaseModel):
    """Dados do cliente (PF ou PJ)."""

    type: PersonType
    document: str = Field(..., description="CPF (11 digits) ou CNPJ (14 digits)")
    name: str = Field(..., max_length=200)
    email: str | None = None
    phone: str | None = None
    mobile: str | None = None
    trade_name: str | None = Field(None, max_length=200, description="PJ only")
    contacts: list[Contact] | None = Field(None, description="PJ only")
    notes: str | None = Field(None, max_length=1000)
    code: str | None = Field(
        None, max_length=50, description="Codigo externo do sistema de origem"
    )
    address: Address | None = None

    model_config = {"extra": "forbid"}


class Service(BaseModel):
    """Servico vinculado a operacao."""

    description: str = Field(..., max_length=500)
    code: str = Field(..., max_length=50)
    price: float | None = Field(None, ge=0)
    cost: float | None = Field(
        None, ge=0, description="Custo do servico (para calculo de margem)"
    )

    model_config = {"extra": "forbid"}


class Sale(BaseModel):
    """Venda avulsa (pagamento unico ou parcela individual)."""

    amount: float = Field(..., gt=0)
    due_date: date
    description: str | None = Field(None, max_length=500)

    model_config = {"extra": "forbid"}


class Contract(BaseModel):
    """Contrato recorrente."""

    start_date: date
    cycles: int | None = Field(None, ge=1, description="null = open-ended (assinatura)")
    frequency: Frequency
    due_day: int = Field(..., ge=1, le=28)
    emission_day: int | None = Field(None, ge=1, le=28)

    model_config = {"extra": "forbid"}


class SaleOperation(BaseModel):
    """Operacao de venda."""

    service: Service
    sale: Sale

    model_config = {"extra": "forbid"}


class ContractOperation(BaseModel):
    """Operacao de contrato."""

    service: Service
    contract: Contract

    model_config = {"extra": "forbid"}


# --- Request body ---


class CanonicalMessage(BaseModel):
    """Payload do POST /api/v1/receivables.

    Compativel com o CDM da CFO Automation API.
    """

    customer: Customer
    operations: list[SaleOperation | ContractOperation] = Field(
        ..., min_length=1, max_length=50
    )
    payment_method: Literal["BOLETO_BANCARIO"]
    notes: str | None = Field(None, max_length=1000)
    date: date | None = Field(None, description="Data de referencia (default: hoje)")

    model_config = {"extra": "forbid"}


# --- Response schemas ---


class CustomerResult(BaseModel):
    """Resultado da criacao/atualizacao do cliente."""

    id: str
    created: bool


class OperationResult(BaseModel):
    """Resultado de uma operacao individual."""

    id: str
    object: Literal["operation"] = "operation"
    type: Literal["sale", "contract"]
    status: OperationStatus
    external_id: str | None = None
    error: str | None = None


class Receivable(BaseModel):
    """Resultado do processamento de um receivable."""

    id: str
    object: Literal["receivable"] = "receivable"
    status: ReceivableStatus
    customer: CustomerResult
    operations: list[OperationResult]
    environment: Literal["live", "test"]
    created_at: str
