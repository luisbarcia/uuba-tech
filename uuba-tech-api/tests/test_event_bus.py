"""Testes do EventBus (Protocol + InMemoryEventBus).

Sem banco de dados — testa publish/subscribe em memória.
"""

import pytest

from app.domain.events.base import DomainEvent
from app.domain.events.event_bus import EventBus
from app.domain.events.fatura_events import FaturaVenceu, PagamentoConfirmado
from app.infrastructure.event_bus import InMemoryEventBus


# --- InMemoryEventBus satisfaz Protocol ---


class TestInMemoryEventBusSatisfazProtocol:
    def test_isinstance_check(self):
        bus = InMemoryEventBus()
        assert isinstance(bus, EventBus)


# --- publish/subscribe ---


class TestPublishSubscribe:
    @pytest.mark.asyncio
    async def test_handler_recebe_evento_publicado(self):
        bus = InMemoryEventBus()
        received: list[DomainEvent] = []

        async def handler(event: FaturaVenceu) -> None:
            received.append(event)

        bus.subscribe(FaturaVenceu, handler)

        evt = FaturaVenceu(
            fatura_id="fat_abc",
            cliente_id="cli_xyz",
            valor_centavos=100000,
            dias_atraso=5,
        )
        await bus.publish(evt)
        assert len(received) == 1
        assert received[0] is evt

    @pytest.mark.asyncio
    async def test_handler_nao_recebe_tipo_diferente(self):
        bus = InMemoryEventBus()
        received: list[DomainEvent] = []

        async def handler(event: FaturaVenceu) -> None:
            received.append(event)

        bus.subscribe(FaturaVenceu, handler)

        evt = PagamentoConfirmado(
            fatura_id="fat_abc",
            cliente_id="cli_xyz",
            valor_centavos=100000,
            meio_pagamento="pix",
        )
        await bus.publish(evt)
        assert len(received) == 0

    @pytest.mark.asyncio
    async def test_multiplos_handlers_mesmo_tipo(self):
        bus = InMemoryEventBus()
        calls: list[str] = []

        async def handler_a(event: FaturaVenceu) -> None:
            calls.append("a")

        async def handler_b(event: FaturaVenceu) -> None:
            calls.append("b")

        bus.subscribe(FaturaVenceu, handler_a)
        bus.subscribe(FaturaVenceu, handler_b)

        await bus.publish(
            FaturaVenceu(
                fatura_id="fat_abc",
                cliente_id="cli_xyz",
                valor_centavos=100000,
                dias_atraso=5,
            )
        )
        assert sorted(calls) == ["a", "b"]

    @pytest.mark.asyncio
    async def test_publish_sem_subscribers_nao_levanta_erro(self):
        bus = InMemoryEventBus()
        evt = FaturaVenceu(
            fatura_id="fat_abc",
            cliente_id="cli_xyz",
            valor_centavos=100000,
            dias_atraso=5,
        )
        await bus.publish(evt)  # Não deve levantar erro


# --- publish_all ---


class TestPublishAll:
    @pytest.mark.asyncio
    async def test_publish_all_publica_lista_de_eventos(self):
        bus = InMemoryEventBus()
        received: list[DomainEvent] = []

        async def handler_v(event: FaturaVenceu) -> None:
            received.append(event)

        async def handler_p(event: PagamentoConfirmado) -> None:
            received.append(event)

        bus.subscribe(FaturaVenceu, handler_v)
        bus.subscribe(PagamentoConfirmado, handler_p)

        events = [
            FaturaVenceu(
                fatura_id="fat_1",
                cliente_id="cli_1",
                valor_centavos=100000,
                dias_atraso=5,
            ),
            PagamentoConfirmado(
                fatura_id="fat_2",
                cliente_id="cli_2",
                valor_centavos=50000,
                meio_pagamento="pix",
            ),
        ]
        await bus.publish_all(events)
        assert len(received) == 2
