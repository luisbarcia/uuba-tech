"""Servico de metricas agregadas da plataforma."""

from datetime import datetime, timezone

from sqlalchemy import func, select, extract
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cliente import Cliente
from app.models.fatura import Fatura
from app.schemas.metricas import MetricasResponse


def _aware(dt: datetime) -> datetime:
    """Garante que datetime tem timezone."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


async def get_metricas(
    db: AsyncSession,
    tenant_id: str | None = None,
) -> MetricasResponse:
    """Calcula metricas agregadas: DSO, revenue, overdue, clientes ativos/inativos."""
    now = datetime.now(timezone.utc)
    current_year = now.year
    current_month = now.month

    # --- Filtros base ---
    fatura_filters = []
    cliente_filters = []
    if tenant_id:
        fatura_filters.append(Fatura.tenant_id == tenant_id)
        cliente_filters.append(Cliente.tenant_id == tenant_id)

    # --- Clientes ativos/inativos ---
    active_q = select(func.count(Cliente.id)).where(Cliente.deletado_em.is_(None), *cliente_filters)
    inactive_q = select(func.count(Cliente.id)).where(
        Cliente.deletado_em.isnot(None), *cliente_filters
    )
    clients_active = (await db.execute(active_q)).scalar() or 0
    clients_inactive = (await db.execute(inactive_q)).scalar() or 0

    # --- Overdue (faturas vencidas) ---
    overdue_count_q = select(func.count(Fatura.id)).where(
        Fatura.status == "vencido", *fatura_filters
    )
    overdue_total_q = select(func.coalesce(func.sum(Fatura.valor), 0)).where(
        Fatura.status == "vencido", *fatura_filters
    )
    overdue_count = (await db.execute(overdue_count_q)).scalar() or 0
    overdue_total_cents = (await db.execute(overdue_total_q)).scalar() or 0

    # --- Revenue mensal (faturas pagas neste mes) ---
    monthly_q = select(func.coalesce(func.sum(Fatura.valor), 0)).where(
        Fatura.status == "pago",
        Fatura.pago_em.isnot(None),
        extract("year", Fatura.pago_em) == current_year,
        extract("month", Fatura.pago_em) == current_month,
        *fatura_filters,
    )
    revenue_monthly_cents = (await db.execute(monthly_q)).scalar() or 0

    # --- Revenue acumulado no ano (faturas pagas este ano) ---
    yearly_q = select(func.coalesce(func.sum(Fatura.valor), 0)).where(
        Fatura.status == "pago",
        Fatura.pago_em.isnot(None),
        extract("year", Fatura.pago_em) == current_year,
        *fatura_filters,
    )
    revenue_accumulated_cents = (await db.execute(yearly_q)).scalar() or 0

    # --- DSO (media de dias entre vencimento e pagamento) ---
    pagas_q = select(Fatura.vencimento, Fatura.pago_em).where(
        Fatura.status == "pago",
        Fatura.pago_em.isnot(None),
        *fatura_filters,
    )
    pagas_result = await db.execute(pagas_q)
    pagas = pagas_result.all()

    dso = 0.0
    if pagas:
        total_dias = sum(
            max(0, (_aware(row.pago_em) - _aware(row.vencimento)).days) for row in pagas
        )
        dso = total_dias / len(pagas)

    return MetricasResponse(
        dso=dso,
        revenue_monthly_cents=revenue_monthly_cents,
        revenue_accumulated_cents=revenue_accumulated_cents,
        overdue_count=overdue_count,
        overdue_total_cents=overdue_total_cents,
        clients_active=clients_active,
        clients_inactive=clients_inactive,
    )
