"""Router de snapshot para deteccao de anomalias."""

from fastapi import APIRouter, Depends, Request
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone

from app.auth.api_key import verify_api_key
from app.database import get_db
from app.models.fatura import Fatura
from app.models.tenant import Tenant

router = APIRouter(
    prefix="/api/v1/watch",
    tags=["watch"],
    dependencies=[Depends(verify_api_key)],
)


@router.get(
    "/snapshot",
    summary="Snapshot para deteccao de anomalias",
    description="Retorna metricas agregadas para comparacao com baselines.",
)
async def get_snapshot(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Snapshot de metricas para o comando `uuba watch`."""
    tenant_id = request.state.tenant_id
    _ = datetime.now(timezone.utc)  # reserved for future 24h metrics

    tenants_count = (
        await db.execute(select(func.count(Tenant.id)).where(Tenant.ativo.is_(True)))
    ).scalar() or 0

    overdue_count = (
        await db.execute(
            select(func.count(Fatura.id)).where(
                and_(
                    Fatura.tenant_id == tenant_id,
                    Fatura.status == "vencido",
                )
            )
        )
    ).scalar() or 0

    return {
        "tenants": tenants_count,
        "keys_created_24h": 0,
        "invoices_overdue": overdue_count,
        "api_latency_avg_ms": 0,
    }
