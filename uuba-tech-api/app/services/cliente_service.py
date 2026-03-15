from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cliente import Cliente
from app.models.fatura import Fatura
from app.schemas.cliente import ClienteCreate, ClienteUpdate, ClienteMetricas
from app.utils.ids import generate_id


async def create_cliente(db: AsyncSession, data: ClienteCreate) -> Cliente:
    cliente = Cliente(id=generate_id("cli"), **data.model_dump())
    db.add(cliente)
    await db.commit()
    await db.refresh(cliente)
    return cliente


async def list_clientes(
    db: AsyncSession,
    telefone: str | None = None,
    order_by: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[Cliente], int]:
    query = select(Cliente)
    if telefone:
        query = query.where(Cliente.telefone == telefone)
    count_q = select(Cliente.id)
    if telefone:
        count_q = count_q.where(Cliente.telefone == telefone)
    total = len((await db.execute(count_q)).all())
    result = await db.execute(query.order_by(Cliente.nome).limit(limit).offset(offset))
    return result.scalars().all(), total


async def get_cliente(db: AsyncSession, cliente_id: str) -> Cliente | None:
    result = await db.execute(select(Cliente).where(Cliente.id == cliente_id))
    return result.scalar_one_or_none()


async def update_cliente(db: AsyncSession, cliente_id: str, data: ClienteUpdate) -> Cliente | None:
    cliente = await get_cliente(db, cliente_id)
    if not cliente:
        return None
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(cliente, key, value)
    await db.commit()
    await db.refresh(cliente)
    return cliente


async def get_metricas(db: AsyncSession, cliente_id: str) -> ClienteMetricas:
    now = datetime.now(timezone.utc)
    result = await db.execute(select(Fatura).where(Fatura.cliente_id == cliente_id))
    faturas = result.scalars().all()

    em_aberto = [f for f in faturas if f.status in ("pendente", "vencido")]
    vencidas = [f for f in em_aberto if f.vencimento < now]

    total_em_aberto = sum(f.valor for f in em_aberto)
    total_vencido = sum(f.valor for f in vencidas)

    dso_dias = 0.0
    pagas = [f for f in faturas if f.status == "pago" and f.pago_em]
    if pagas:
        total_dias = sum((f.pago_em - f.vencimento).days for f in pagas)
        dso_dias = total_dias / len(pagas)

    return ClienteMetricas(
        dso_dias=dso_dias,
        total_em_aberto=total_em_aberto,
        total_vencido=total_vencido,
        faturas_em_aberto=len(em_aberto),
        faturas_vencidas=len(vencidas),
    )
