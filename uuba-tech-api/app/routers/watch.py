"""Router de snapshot para deteccao de anomalias."""

from fastapi import APIRouter, Depends, Request
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.api_key import require_permission, verify_api_key
from app.database import get_db
from app.models.fatura import Fatura
from app.models.cliente import Cliente

router = APIRouter(
    prefix="/api/v1/watch",
    tags=["watch"],
    dependencies=[Depends(verify_api_key), Depends(require_permission("admin:read"))],
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

    clients_count = (
        await db.execute(
            select(func.count(Cliente.id)).where(
                and_(Cliente.tenant_id == tenant_id, Cliente.deletado_em.is_(None))
            )
        )
    ).scalar() or 0

    overdue_count = (
        await db.execute(
            select(func.count(Fatura.id)).where(
                and_(Fatura.tenant_id == tenant_id, Fatura.status == "vencido")
            )
        )
    ).scalar() or 0

    return {
        "tenants": 1,
        "clients_active": clients_count,
        "keys_created_24h": 0,
        "invoices_overdue": overdue_count,
        "api_latency_avg_ms": 0,
    }
