from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.fatura import Fatura
from app.schemas.fatura import FaturaCreate, FaturaUpdate
from app.utils.ids import generate_id


async def create_fatura(db: AsyncSession, data: FaturaCreate) -> Fatura:
    fatura = Fatura(id=generate_id("fat"), **data.model_dump())
    db.add(fatura)
    await db.commit()
    await db.refresh(fatura)
    return fatura


async def list_faturas(
    db: AsyncSession,
    status: str | None = None,
    cliente_id: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[Fatura], int]:
    query = select(Fatura)
    if status:
        statuses = [s.strip() for s in status.split(",")]
        query = query.where(Fatura.status.in_(statuses))
    if cliente_id:
        query = query.where(Fatura.cliente_id == cliente_id)

    count_q = select(Fatura.id)
    if status:
        count_q = count_q.where(Fatura.status.in_([s.strip() for s in status.split(",")]))
    if cliente_id:
        count_q = count_q.where(Fatura.cliente_id == cliente_id)
    total = len((await db.execute(count_q)).all())

    result = await db.execute(query.order_by(Fatura.vencimento).limit(limit).offset(offset))
    return result.scalars().all(), total


async def get_fatura(db: AsyncSession, fatura_id: str) -> Fatura | None:
    result = await db.execute(select(Fatura).where(Fatura.id == fatura_id))
    return result.scalar_one_or_none()


async def update_fatura(db: AsyncSession, fatura_id: str, data: FaturaUpdate) -> Fatura | None:
    fatura = await get_fatura(db, fatura_id)
    if not fatura:
        return None
    update_data = data.model_dump(exclude_unset=True)
    if "status" in update_data and update_data["status"] == "pago":
        update_data["pago_em"] = datetime.now(timezone.utc)
    for key, value in update_data.items():
        setattr(fatura, key, value)
    await db.commit()
    await db.refresh(fatura)
    return fatura
