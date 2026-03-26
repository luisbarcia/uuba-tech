"""Schema para metricas agregadas da plataforma."""

from pydantic import BaseModel, Field


class MetricasResponse(BaseModel):
    """Metricas agregadas do dashboard."""

    dso: float = Field(
        default=0.0,
        description="Days Sales Outstanding — media de dias para recebimento",
    )
    revenue_monthly_cents: int = Field(
        default=0,
        description="Revenue do mes atual em centavos",
    )
    revenue_accumulated_cents: int = Field(
        default=0,
        description="Revenue acumulado no ano em centavos",
    )
    overdue_count: int = Field(
        default=0,
        description="Quantidade de faturas vencidas",
    )
    overdue_total_cents: int = Field(
        default=0,
        description="Valor total vencido em centavos",
    )
    clients_active: int = Field(
        default=0,
        description="Clientes ativos",
    )
    clients_inactive: int = Field(
        default=0,
        description="Clientes inativos (anonimizados)",
    )
