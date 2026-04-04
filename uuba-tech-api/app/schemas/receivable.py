"""Schemas do endpoint POST /api/v1/receivables — Canonical Data Model.

Compativel com o payload da CFO Automation API (cfo-api).
Permite migracao transparente: cliente muda URL + API key, payload identico.

Fonte: openapi/components/schemas/canonical.yaml do repo cfo-automation-api.
"""

from datetime import date
from enum import Enum
from typing import Literal, Optional, Union

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
    email: Optional[str] = None
    phone: Optional[str] = None
    mobile: Optional[str] = None
    role: Optional[str] = Field(None, max_length=100)

    model_config = {"extra": "forbid"}


class Address(BaseModel):
    """Endereco do cliente."""

    street: Optional[str] = Field(None, max_length=200)
    number: Optional[str] = Field(None, max_length=20)
    complement: Optional[str] = Field(None, max_length=100)
    neighborhood: Optional[str] = Field(None, max_length=100)
    zip_code: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[BrazilianState] = None

    model_config = {"extra": "forbid"}


class Customer(BaseModel):
    """Dados do cliente (PF ou PJ)."""

    type: PersonType
    document: str = Field(..., description="CPF (11 digits) ou CNPJ (14 digits)")
    name: str = Field(..., max_length=200)
    email: Optional[str] = None
    phone: Optional[str] = None
    mobile: Optional[str] = None
    trade_name: Optional[str] = Field(None, max_length=200, description="PJ only")
    contacts: Optional[list[Contact]] = Field(None, description="PJ only")
    notes: Optional[str] = Field(None, max_length=1000)
    code: Optional[str] = Field(
        None, max_length=50, description="Codigo externo do sistema de origem"
    )
    address: Optional[Address] = None

    model_config = {"extra": "forbid"}


class Service(BaseModel):
    """Servico vinculado a operacao."""

    description: str = Field(..., max_length=500)
    code: str = Field(..., max_length=50)
    price: Optional[float] = Field(None, ge=0)
    cost: Optional[float] = Field(
        None, ge=0, description="Custo do servico (para calculo de margem)"
    )

    model_config = {"extra": "forbid"}


class Sale(BaseModel):
    """Venda avulsa (pagamento unico ou parcela individual)."""

    amount: float = Field(..., gt=0)
    due_date: date
    description: Optional[str] = Field(None, max_length=500)

    model_config = {"extra": "forbid"}


class Contract(BaseModel):
    """Contrato recorrente."""

    start_date: date
    cycles: Optional[int] = Field(None, ge=1, description="null = open-ended (assinatura)")
    frequency: Frequency
    due_day: int = Field(..., ge=1, le=28)
    emission_day: Optional[int] = Field(None, ge=1, le=28)

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
    operations: list[Union[SaleOperation, ContractOperation]] = Field(
        ..., min_length=1, max_length=50
    )
    payment_method: Literal["BOLETO_BANCARIO"]
    notes: Optional[str] = Field(None, max_length=1000)
    date: Optional[date] = Field(None, description="Data de referencia (default: hoje)")

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
    external_id: Optional[str] = None
    error: Optional[str] = None


class Receivable(BaseModel):
    """Resultado do processamento de um receivable."""

    id: str
    object: Literal["receivable"] = "receivable"
    status: ReceivableStatus
    customer: CustomerResult
    operations: list[OperationResult]
    environment: Literal["live", "test"]
    created_at: str
