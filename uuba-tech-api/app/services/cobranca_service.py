import re
from datetime import datetime, timezone, timedelta
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cobranca import Cobranca
from app.schemas.cobranca import CobrancaCreate
from app.exceptions import APIError
from app.utils.ids import generate_id
from app.domain.value_objects.cobranca_enums import CobrancaStatus


async def create_cobranca(db: AsyncSession, data: CobrancaCreate) -> Cobranca:
    """Registra uma nova cobrança com timestamp de envio. Levanta APIError 409 se fatura ou cliente não existir."""
    cobranca = Cobranca(
        id=generate_id("cob"),
        enviado_em=datetime.now(timezone.utc),
        **data.model_dump(),
    )
    db.add(cobranca)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise APIError(
            409,
            "integridade",
            "Erro de integridade",
            f"Fatura {data.fatura_id} ou cliente {data.cliente_id} não existe.",
        )
    await db.refresh(cobranca)
    return cobranca


async def list_cobrancas(
    db: AsyncSession,
    periodo: str | None = None,
    cliente_id: str | None = None,
    fatura_id: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[Cobranca], int]:
    """Lista cobranças com paginação. Filtra por período (ex: '7d'), cliente_id e/ou fatura_id.

    Args:
        periodo: Formato 'Nd' (ex: '7d', '30d'). Levanta APIError 422 se inválido.

    Returns:
        Tupla (lista de cobranças, total de registros).
    """
    query = select(Cobranca)
    if periodo:
        match = re.fullmatch(r"(\d+)d", periodo)
        if not match:
            raise APIError(
                422,
                "periodo-invalido",
                "Formato de período inválido",
                f"Use o formato Nd (ex: 7d, 30d). Recebido: '{periodo}'.",
            )
        days = int(match.group(1))
        since = datetime.now(timezone.utc) - timedelta(days=days)
        query = query.where(Cobranca.created_at >= since)
    if cliente_id:
        query = query.where(Cobranca.cliente_id == cliente_id)
    if fatura_id:
        query = query.where(Cobranca.fatura_id == fatura_id)

    count_q = select(func.count(Cobranca.id))
    if periodo:
        count_q = count_q.where(Cobranca.created_at >= since)
    if cliente_id:
        count_q = count_q.where(Cobranca.cliente_id == cliente_id)
    if fatura_id:
        count_q = count_q.where(Cobranca.fatura_id == fatura_id)
    total = (await db.execute(count_q)).scalar() or 0

    result = await db.execute(
        query.order_by(Cobranca.created_at.desc()).limit(limit).offset(offset)
    )
    return result.scalars().all(), total


async def get_historico(db: AsyncSession, fatura_id: str) -> list[Cobranca]:
    """Retorna histórico de cobranças de uma fatura, ordenado da mais recente para a mais antiga."""
    result = await db.execute(
        select(Cobranca).where(Cobranca.fatura_id == fatura_id).order_by(Cobranca.created_at.desc())
    )
    return result.scalars().all()


async def pausar(db: AsyncSession, cobranca_id: str) -> Cobranca | None:
    """Pausa uma cobrança (status -> 'pausado'). Retorna None se não encontrada."""
    result = await db.execute(select(Cobranca).where(Cobranca.id == cobranca_id))
    cobranca = result.scalar_one_or_none()
    if not cobranca:
        return None
    cobranca.pausado = True
    cobranca.status = CobrancaStatus.PAUSADO.value
    await db.commit()
    await db.refresh(cobranca)
    return cobranca


async def retomar(db: AsyncSession, cobranca_id: str) -> Cobranca | None:
    """Retoma uma cobrança pausada (status -> 'enviado'). Retorna None se não encontrada."""
    result = await db.execute(select(Cobranca).where(Cobranca.id == cobranca_id))
    cobranca = result.scalar_one_or_none()
    if not cobranca:
        return None
    cobranca.pausado = False
    cobranca.status = CobrancaStatus.ENVIADO.value
    await db.commit()
    await db.refresh(cobranca)
    return cobranca
