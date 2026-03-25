"""Serviço de faturas.

Transições de status delegadas ao FaturaAggregate (DP-02).
Persistência delegada ao FaturaRepository (DP-04).
Domain Events publicados via EventBus (DP-03).
"""

from app.domain.aggregates.fatura import FaturaAggregate
from app.domain.events.event_bus import EventBus
from app.domain.repositories.fatura_repository import FaturaRepository
from app.domain.value_objects.fatura_status import FaturaStatus
from app.models.fatura import Fatura
from app.schemas.fatura import FaturaCreate, FaturaUpdate
from app.utils.ids import generate_id


async def create_fatura(repo: FaturaRepository, data: FaturaCreate) -> Fatura:
    """Cria uma nova fatura. Levanta APIError 409 se cliente_id não existir."""
    fatura = Fatura(id=generate_id("fat"), **data.model_dump())
    return await repo.create(fatura)


async def list_faturas(
    repo: FaturaRepository,
    status: str | None = None,
    cliente_id: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[Fatura], int]:
    """Lista faturas com paginação e filtros.

    Returns:
        Tupla (lista de faturas, total de registros).
    """
    return await repo.list_by_filters(
        status=status, cliente_id=cliente_id, limit=limit, offset=offset
    )


async def get_fatura(repo: FaturaRepository, fatura_id: str) -> Fatura | None:
    """Busca fatura por ID. Retorna None se não encontrada."""
    return await repo.get_by_id(fatura_id)


async def update_fatura(
    repo: FaturaRepository,
    fatura_id: str,
    data: FaturaUpdate,
    event_bus: EventBus | None = None,
) -> Fatura | None:
    """Atualiza fatura (patch parcial). Valida transições via FaturaAggregate (DP-02).

    Publica domain events via EventBus (DP-03) após persistência.

    Raises:
        APIError 409: Se a transição de status for inválida.
    """
    fatura = await repo.get_by_id(fatura_id)
    if not fatura:
        return None
    update_data = data.model_dump(exclude_unset=True, mode="python")
    pending_events = []
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
        pending_events = aggregate.collect_events()
        update_data["status"] = aggregate.status.value
        if aggregate.pago_em and not fatura.pago_em:
            update_data["pago_em"] = aggregate.pago_em
    for key, value in update_data.items():
        setattr(fatura, key, value)
    result = await repo.update(fatura)
    if event_bus and pending_events:
        await event_bus.publish_all(pending_events)
    return result


async def transicionar_faturas_vencidas(repo: FaturaRepository) -> int:
    """Transiciona faturas pendentes com vencimento ultrapassado para 'vencido'.

    Job idempotente: só atua em status='pendente'.

    Returns:
        Quantidade de faturas transicionadas.
    """
    return await repo.bulk_transicionar_vencidas()
