"""Router de uso da API baseado no audit log."""

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone, timedelta

from app.auth.api_key import verify_api_key
from app.database import get_db
from app.models.audit_log import AuditLog

router = APIRouter(
    prefix="/api/v1/usage",
    tags=["usage"],
    dependencies=[Depends(verify_api_key)],
)


@router.get(
    "",
    summary="Rastreamento de uso da API",
    description="Retorna entradas de uso agregadas do audit log.",
)
async def get_usage(
    request: Request,
    tenant_id: str | None = Query(None, description="Filtrar por tenant"),
    days: int = Query(30, ge=1, le=365, description="Periodo em dias"),
    db: AsyncSession = Depends(get_db),
):
    """Retorna uso da API nos ultimos N dias."""
    tid = tenant_id or request.state.tenant_id
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    query = (
        select(AuditLog)
        .where(
            and_(
                AuditLog.tenant_id == tid,
                AuditLog.created_at >= cutoff,
            )
        )
        .order_by(AuditLog.created_at.desc())
    )

    result = await db.execute(query)
    entries = result.scalars().all()

    return [
        {
            "tenant_id": e.tenant_id,
            "endpoint": e.recurso,
            "method": e.acao,
            "status_code": 200,
            "latency_ms": 0,
            "created_at": e.created_at.isoformat() if e.created_at else "",
        }
        for e in entries
    ]
