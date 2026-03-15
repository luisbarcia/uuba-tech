from datetime import datetime, timezone, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cobranca import Cobranca
from app.schemas.cobranca import CobrancaCreate
from app.utils.ids import generate_id


async def create_cobranca(db: AsyncSession, data: CobrancaCreate) -> Cobranca:
    cobranca = Cobranca(
        id=generate_id("cob"),
        enviado_em=datetime.now(timezone.utc),
        **data.model_dump(),
    )
    db.add(cobranca)
    await db.commit()
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
    query = select(Cobranca)
    if periodo:
        days = int(periodo.replace("d", ""))
        since = datetime.now(timezone.utc) - timedelta(days=days)
        query = query.where(Cobranca.created_at >= since)
    if cliente_id:
        query = query.where(Cobranca.cliente_id == cliente_id)
    if fatura_id:
        query = query.where(Cobranca.fatura_id == fatura_id)

    count_q = select(Cobranca.id)
    if periodo:
        days = int(periodo.replace("d", ""))
        since = datetime.now(timezone.utc) - timedelta(days=days)
        count_q = count_q.where(Cobranca.created_at >= since)
    if cliente_id:
        count_q = count_q.where(Cobranca.cliente_id == cliente_id)
    if fatura_id:
        count_q = count_q.where(Cobranca.fatura_id == fatura_id)
    total = len((await db.execute(count_q)).all())

    result = await db.execute(query.order_by(Cobranca.created_at.desc()).limit(limit).offset(offset))
    return result.scalars().all(), total


async def get_historico(db: AsyncSession, fatura_id: str) -> list[Cobranca]:
    result = await db.execute(
        select(Cobranca)
        .where(Cobranca.fatura_id == fatura_id)
        .order_by(Cobranca.created_at.desc())
    )
    return result.scalars().all()


async def pausar(db: AsyncSession, cobranca_id: str) -> Cobranca | None:
    result = await db.execute(select(Cobranca).where(Cobranca.id == cobranca_id))
    cobranca = result.scalar_one_or_none()
    if not cobranca:
        return None
    cobranca.pausado = True
    cobranca.status = "pausado"
    await db.commit()
    await db.refresh(cobranca)
    return cobranca


async def retomar(db: AsyncSession, cobranca_id: str) -> Cobranca | None:
    result = await db.execute(select(Cobranca).where(Cobranca.id == cobranca_id))
    cobranca = result.scalar_one_or_none()
    if not cobranca:
        return None
    cobranca.pausado = False
    cobranca.status = "enviado"
    await db.commit()
    await db.refresh(cobranca)
    return cobranca
