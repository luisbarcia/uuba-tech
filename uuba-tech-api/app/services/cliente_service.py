"""Serviço de clientes.

Persistência delegada ao ClienteRepository (DP-04).
"""

from datetime import datetime, timezone

from app.models.cliente import Cliente
from app.schemas.cliente import ClienteCreate, ClienteUpdate, ClienteMetricas
from app.utils.ids import generate_id
from app.domain.repositories.cliente_repository import ClienteRepository
from app.domain.repositories.fatura_repository import FaturaRepository


def _aware(dt: datetime) -> datetime:
    """Garante que datetime tem timezone (defensivo contra DBs que retornam naive)."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


async def create_cliente(repo: ClienteRepository, data: ClienteCreate) -> Cliente:
    """Cria um novo cliente. Levanta APIError 409 se documento já existir."""
    cliente = Cliente(id=generate_id("cli"), **data.model_dump())
    return await repo.create(cliente)


async def list_clientes(
    repo: ClienteRepository,
    telefone: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[Cliente], int]:
    """Lista clientes com paginação.

    Returns:
        Tupla (lista de clientes, total de registros).
    """
    return await repo.list_by_filters(telefone=telefone, limit=limit, offset=offset)


async def get_cliente(repo: ClienteRepository, cliente_id: str) -> Cliente | None:
    """Busca cliente por ID. Retorna None se não encontrado."""
    return await repo.get_by_id(cliente_id)


async def update_cliente(
    repo: ClienteRepository, cliente_id: str, data: ClienteUpdate
) -> Cliente | None:
    """Atualiza campos do cliente (patch parcial). Retorna None se não encontrado."""
    cliente = await repo.get_by_id(cliente_id)
    if not cliente:
        return None
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(cliente, key, value)
    return await repo.update(cliente)


async def get_metricas(fatura_repo: FaturaRepository, cliente_id: str) -> ClienteMetricas:
    """Calcula métricas financeiras do cliente: DSO, total em aberto, faturas vencidas."""
    now = datetime.now(timezone.utc)
    faturas_list, _ = await fatura_repo.list_by_filters(cliente_id=cliente_id, limit=10000)

    em_aberto = [f for f in faturas_list if f.status in ("pendente", "vencido")]
    vencidas = [f for f in em_aberto if _aware(f.vencimento) < now]

    total_em_aberto = sum(f.valor for f in em_aberto)
    total_vencido = sum(f.valor for f in vencidas)

    dso_dias = 0.0
    pagas = [f for f in faturas_list if f.status == "pago" and f.pago_em]
    if pagas:
        total_dias = sum((_aware(f.pago_em) - _aware(f.vencimento)).days for f in pagas)
        dso_dias = total_dias / len(pagas)

    return ClienteMetricas(
        dso_dias=dso_dias,
        total_em_aberto=total_em_aberto,
        total_vencido=total_vencido,
        faturas_em_aberto=len(em_aberto),
        faturas_vencidas=len(vencidas),
    )
