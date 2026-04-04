"""Router de logs da plataforma baseado no audit_log."""

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.auth.api_key import require_permission, verify_api_key
from app.database import get_db
from app.models.audit_log import AuditLog

router = APIRouter(
    prefix="/api/v1/logs",
    tags=["logs"],
    dependencies=[Depends(verify_api_key), Depends(require_permission("admin:read"))],
)


def _to_log_entry(row: AuditLog) -> dict:
    return {
        "timestamp": row.created_at.isoformat() if row.created_at else "",
        "level": "info",
        "message": f"{row.acao} {row.recurso}" + (f" {row.recurso_id}" if row.recurso_id else ""),
        "service": "api",
    }


@router.get(
    "",
    summary="Listar logs recentes",
    description="Retorna entradas do audit log como log entries.",
)
async def list_logs(
    request: Request,
    limit: int = Query(20, ge=1, le=100),
    level: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Lista logs recentes do audit trail."""
    tenant_id = request.state.tenant_id
    query = select(AuditLog).where(AuditLog.tenant_id == tenant_id)
    query = query.order_by(AuditLog.created_at.desc()).limit(limit)
    result = await db.execute(query)
    return [_to_log_entry(row) for row in result.scalars().all()]


@router.get(
    "/search",
    summary="Buscar nos logs",
    description="Busca textual nas entradas do audit log.",
)
async def search_logs(
    request: Request,
    q: str = Query(..., description="Termo de busca"),
    limit: int = Query(50, ge=1, le=100),
    level: str | None = Query(None),
    since: str | None = Query(None, description="Data inicio (ISO 8601)"),
    until: str | None = Query(None, description="Data fim (ISO 8601)"),
    db: AsyncSession = Depends(get_db),
):
    """Busca textual nos logs."""
    tenant_id = request.state.tenant_id
    filters = [AuditLog.tenant_id == tenant_id]

    escaped_q = q.replace("%", r"\%").replace("_", r"\_")
    search_pattern = f"%{escaped_q}%"
    filters.append(
        AuditLog.acao.ilike(search_pattern)
        | AuditLog.recurso.ilike(search_pattern)
        | AuditLog.detalhes.ilike(search_pattern)
    )

    if since:
        filters.append(AuditLog.created_at >= datetime.fromisoformat(since))
    if until:
        filters.append(AuditLog.created_at <= datetime.fromisoformat(until))

    query = select(AuditLog).where(and_(*filters)).order_by(AuditLog.created_at.desc()).limit(limit)
    result = await db.execute(query)
    return [_to_log_entry(row) for row in result.scalars().all()]
