"""Router de metricas agregadas — dashboard da plataforma."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.api_key import verify_api_key
from app.database import get_db
from app.schemas.metricas import MetricasResponse
from app.services import metricas_service

router = APIRouter(
    prefix="/api/v1/metricas",
    tags=["metricas"],
    dependencies=[Depends(verify_api_key)],
)


@router.get(
    "",
    response_model=MetricasResponse,
    summary="Metricas agregadas",
    description="Retorna metricas agregadas da plataforma: DSO, revenue, overdue, clientes.",
)
async def get_metricas(
    tenant_id: str | None = Query(None, description="Filtrar por tenant"),
    db: AsyncSession = Depends(get_db),
):
    """Retorna metricas agregadas da plataforma."""
    return await metricas_service.get_metricas(db, tenant_id=tenant_id)
