"""Router de metricas agregadas — dashboard da plataforma."""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.api_key import require_permission, verify_api_key
from app.database import get_db
from app.schemas.metricas import MetricasResponse
from app.services import metricas_service

router = APIRouter(
    prefix="/api/v1/metricas",
    tags=["metricas"],
    dependencies=[Depends(verify_api_key), Depends(require_permission("metrics:read"))],
)


@router.get(
    "",
    response_model=MetricasResponse,
    summary="Metricas agregadas",
    description="Retorna metricas agregadas do tenant autenticado: DSO, revenue, overdue, clientes.",
)
async def get_metricas(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Retorna metricas agregadas do tenant autenticado."""
    tenant_id = request.state.tenant_id
    return await metricas_service.get_metricas(db, tenant_id=tenant_id)
