"""Serviço de cobranças.

Invariante: fatura em status terminal não aceita novas cobranças (DP-02).
Persistência delegada aos repositories (DP-04).
Domain Events publicados via EventBus (DP-03).
"""

from datetime import datetime, timezone

from app.domain.aggregates.fatura import FaturaAggregate
from app.domain.events.event_bus import EventBus
from app.domain.events.fatura_events import CobrancaEnviada
from app.domain.repositories.cobranca_repository import CobrancaRepository
from app.domain.repositories.fatura_repository import FaturaRepository
from app.domain.value_objects.cobranca_enums import CobrancaStatus
from app.exceptions import APIError
from app.models.cobranca import Cobranca
from app.schemas.cobranca import CobrancaCreate
from app.utils.ids import generate_id


async def create_cobranca(
    cobranca_repo: CobrancaRepository,
    fatura_repo: FaturaRepository,
    data: CobrancaCreate,
    event_bus: EventBus | None = None,
) -> Cobranca:
    """Registra uma nova cobrança. Verifica invariante do aggregate antes de persistir.

    Publica CobrancaEnviada via EventBus (DP-03) após persistência.

    Raises:
        APIError 409: Se fatura está em status terminal ou FK inválida.
    """
    fatura = await fatura_repo.get_by_id(data.fatura_id)
    if fatura:
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
        if not aggregate.pode_receber_cobranca():
            raise APIError(
                409,
                "fatura-terminal",
                "Fatura em status terminal",
                f"Fatura {data.fatura_id} está '{aggregate.status.value}' "
                f"e não aceita novas cobranças.",
            )
    cobranca = Cobranca(
        id=generate_id("cob"),
        enviado_em=datetime.now(timezone.utc),
        **data.model_dump(),
    )
    result = await cobranca_repo.create(cobranca)
    if event_bus:
        await event_bus.publish(
            CobrancaEnviada(
                cobranca_id=result.id,
                fatura_id=data.fatura_id,
                cliente_id=data.cliente_id,
                canal=data.canal,
                tom=data.tom or "",
            )
        )
    return result


async def list_cobrancas(
    repo: CobrancaRepository,
    periodo: str | None = None,
    cliente_id: str | None = None,
    fatura_id: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[Cobranca], int]:
    """Lista cobranças com paginação e filtros.

    Returns:
        Tupla (lista de cobranças, total de registros).
    """
    return await repo.list_by_filters(
        periodo=periodo,
        cliente_id=cliente_id,
        fatura_id=fatura_id,
        limit=limit,
        offset=offset,
    )


async def get_historico(repo: CobrancaRepository, fatura_id: str) -> list[Cobranca]:
    """Retorna histórico de cobranças de uma fatura."""
    return await repo.list_by_fatura(fatura_id)


async def pausar(repo: CobrancaRepository, cobranca_id: str) -> Cobranca | None:
    """Pausa uma cobrança (status -> 'pausado'). Retorna None se não encontrada."""
    cobranca = await repo.get_by_id(cobranca_id)
    if not cobranca:
        return None
    cobranca.pausado = True
    cobranca.status = CobrancaStatus.PAUSADO.value
    return await repo.update(cobranca)


async def retomar(repo: CobrancaRepository, cobranca_id: str) -> Cobranca | None:
    """Retoma uma cobrança pausada (status -> 'enviado'). Retorna None se não encontrada."""
    cobranca = await repo.get_by_id(cobranca_id)
    if not cobranca:
        return None
    cobranca.pausado = False
    cobranca.status = CobrancaStatus.ENVIADO.value
    return await repo.update(cobranca)
