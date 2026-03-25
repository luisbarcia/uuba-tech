"""Serviço de faturas.

Transições de status delegadas ao FaturaAggregate (DP-02).
"""

import logging
from datetime import datetime, timezone

from sqlalchemy import select, func, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.fatura import Fatura
from app.schemas.fatura import FaturaCreate, FaturaUpdate
from app.exceptions import APIError
from app.utils.ids import generate_id
from app.domain.value_objects.fatura_status import FaturaStatus
from app.domain.aggregates.fatura import FaturaAggregate

logger = logging.getLogger("uuba")


async def create_fatura(db: AsyncSession, data: FaturaCreate) -> Fatura:
    """Cria uma nova fatura. Levanta APIError 409 se cliente_id não existir."""
    fatura = Fatura(id=generate_id("fat"), **data.model_dump())
    db.add(fatura)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise APIError(
            409,
            "integridade",
            "Erro de integridade",
            f"Cliente {data.cliente_id} não existe ou violação de constraint.",
        )
    await db.refresh(fatura)
    return fatura


def _apply_fatura_filters(query, status: str | None, cliente_id: str | None):
    if status:
        statuses = [s.strip() for s in status.split(",")]
        query = query.where(Fatura.status.in_(statuses))
    if cliente_id:
        query = query.where(Fatura.cliente_id == cliente_id)
    return query


async def list_faturas(
    db: AsyncSession,
    status: str | None = None,
    cliente_id: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[Fatura], int]:
    """Lista faturas com paginação. Filtra por status (aceita múltiplos separados por vírgula) e/ou cliente_id.

    Returns:
        Tupla (lista de faturas, total de registros).
    """
    query = _apply_fatura_filters(select(Fatura), status, cliente_id)
    count_q = _apply_fatura_filters(select(func.count(Fatura.id)), status, cliente_id)
    total = (await db.execute(count_q)).scalar() or 0

    result = await db.execute(query.order_by(Fatura.vencimento).limit(limit).offset(offset))
    return result.scalars().all(), total


async def get_fatura(db: AsyncSession, fatura_id: str) -> Fatura | None:
    """Busca fatura por ID. Retorna None se não encontrada."""
    result = await db.execute(select(Fatura).where(Fatura.id == fatura_id))
    return result.scalar_one_or_none()


async def update_fatura(db: AsyncSession, fatura_id: str, data: FaturaUpdate) -> Fatura | None:
    """Atualiza fatura (patch parcial). Valida transições via FaturaAggregate (DP-02).

    Raises:
        APIError 409: Se a transição de status for inválida.
    """
    fatura = await get_fatura(db, fatura_id)
    if not fatura:
        return None
    update_data = data.model_dump(exclude_unset=True, mode="python")
    if "status" in update_data:
        novo = (
            update_data["status"]
            if isinstance(update_data["status"], FaturaStatus)
            else FaturaStatus(update_data["status"])
        )
        aggregate = FaturaAggregate.from_primitives(
            id=fatura.id,
            cliente_id=fatura.cliente_id,
            valor=fatura.valor,
            moeda=fatura.moeda,
            status=fatura.status,
            vencimento=fatura.vencimento,
            descricao=fatura.descricao,
            numero_nf=fatura.numero_nf,
            pagamento_link=fatura.pagamento_link,
            pago_em=fatura.pago_em,
            promessa_pagamento=fatura.promessa_pagamento,
        )
        aggregate.transicionar(novo)  # levanta APIError se inválido
        update_data["status"] = aggregate.status.value
        if aggregate.pago_em and not fatura.pago_em:
            update_data["pago_em"] = aggregate.pago_em
    for key, value in update_data.items():
        setattr(fatura, key, value)
    await db.commit()
    await db.refresh(fatura)
    return fatura


async def transicionar_faturas_vencidas(db: AsyncSession) -> int:
    """Transiciona faturas pendentes com vencimento ultrapassado para 'vencido'.

    Job idempotente (FR-015): só atua em status='pendente', então rodar múltiplas
    vezes no mesmo dia não gera efeitos colaterais. Faturas em 'em_negociacao'
    ou outros status não são afetadas (AC-020).

    Returns:
        Quantidade de faturas transicionadas.
    """
    now = datetime.now(timezone.utc)
    stmt = (
        update(Fatura)
        .where(Fatura.status == FaturaStatus.PENDENTE.value)
        .where(Fatura.vencimento < now)
        .values(status=FaturaStatus.VENCIDO.value, updated_at=now)
    )
    result = await db.execute(stmt)
    await db.commit()
    count = result.rowcount
    logger.info(f"transicionar_faturas_vencidas: {count} fatura(s) pendente→vencido")
    return count
