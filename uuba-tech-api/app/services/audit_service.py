"""Serviço de audit trail (LGPD Art. 37).

Registra operações de tratamento de dados pessoais.
"""

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog
from app.utils.ids import generate_id


async def registrar(
    session: AsyncSession,
    *,
    tenant_id: str,
    acao: str,
    recurso: str,
    recurso_id: str | None = None,
    detalhes: str | None = None,
    ip_address: str | None = None,
) -> None:
    """Registra uma operação no audit log."""
    log = AuditLog(
        id=generate_id("aud"),
        tenant_id=tenant_id,
        acao=acao,
        recurso=recurso,
        recurso_id=recurso_id,
        detalhes=detalhes,
        ip_address=ip_address,
    )
    session.add(log)
    await session.commit()


async def listar(
    session: AsyncSession,
    *,
    tenant_id: str,
    recurso: str | None = None,
    recurso_id: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[AuditLog], int]:
    """Lista registros de auditoria filtrados por tenant."""
    query = select(AuditLog).where(AuditLog.tenant_id == tenant_id)
    count_q = select(func.count(AuditLog.id)).where(AuditLog.tenant_id == tenant_id)

    if recurso:
        query = query.where(AuditLog.recurso == recurso)
        count_q = count_q.where(AuditLog.recurso == recurso)
    if recurso_id:
        query = query.where(AuditLog.recurso_id == recurso_id)
        count_q = count_q.where(AuditLog.recurso_id == recurso_id)

    total = (await session.execute(count_q)).scalar() or 0
    result = await session.execute(
        query.order_by(AuditLog.created_at.desc()).limit(limit).offset(offset)
    )
    return result.scalars().all(), total
