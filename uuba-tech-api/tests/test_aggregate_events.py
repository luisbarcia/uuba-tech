"""Testes de emissão de Domain Events pelo FaturaAggregate.

Verifica que transições de estado emitem os eventos corretos.
"""

from datetime import datetime, timezone

import pytest

from app.domain.aggregates.fatura import FaturaAggregate
from app.domain.events.base import DomainEvent
from app.domain.events.fatura_events import FaturaVenceu, PagamentoConfirmado
from app.domain.value_objects.fatura_status import FaturaStatus


def _make_aggregate(status: str = "pendente", **overrides) -> FaturaAggregate:
    defaults = dict(
        id="fat_test1",
        cliente_id="cli_test1",
        valor=100000,
        moeda="BRL",
        status=status,
        vencimento=datetime(2026, 3, 20, tzinfo=timezone.utc),
        descricao=None,
        numero_nf=None,
        pagamento_link=None,
        pago_em=None,
        promessa_pagamento=None,
    )
    defaults.update(overrides)
    return FaturaAggregate.from_primitives(**defaults)


# --- collect_events / clear ---


class TestEventCollection:
    def test_aggregate_novo_sem_eventos(self):
        agg = _make_aggregate()
        assert agg.collect_events() == []

    def test_collect_events_retorna_e_limpa(self):
        agg = _make_aggregate(status="pendente")
        agg.transicionar(FaturaStatus.VENCIDO)
        events = agg.collect_events()
        assert len(events) == 1
        # Segunda chamada retorna vazio
        assert agg.collect_events() == []

    def test_eventos_sao_domain_events(self):
        agg = _make_aggregate(status="pendente")
        agg.transicionar(FaturaStatus.VENCIDO)
        events = agg.collect_events()
        assert all(isinstance(e, DomainEvent) for e in events)


# --- FaturaVenceu emitido em transição pendente→vencido ---


class TestFaturaVenceuEvent:
    def test_transicao_para_vencido_emite_evento(self):
        agg = _make_aggregate(status="pendente")
        agg.transicionar(FaturaStatus.VENCIDO)
        events = agg.collect_events()
        assert len(events) == 1
        assert isinstance(events[0], FaturaVenceu)

    def test_evento_contem_dados_corretos(self):
        agg = _make_aggregate(
            status="pendente",
            id="fat_abc",
            cliente_id="cli_xyz",
            valor=250000,
            vencimento=datetime(2026, 3, 20, tzinfo=timezone.utc),
        )
        agg.transicionar(FaturaStatus.VENCIDO)
        evt = agg.collect_events()[0]
        assert isinstance(evt, FaturaVenceu)
        assert evt.fatura_id == "fat_abc"
        assert evt.cliente_id == "cli_xyz"
        assert evt.valor_centavos == 250000

    def test_dias_atraso_calculado(self):
        """dias_atraso deve ser >= 0 (calculado no momento da emissão)."""
        agg = _make_aggregate(
            status="pendente",
            vencimento=datetime(2026, 3, 20, tzinfo=timezone.utc),
        )
        agg.transicionar(FaturaStatus.VENCIDO)
        evt = agg.collect_events()[0]
        assert isinstance(evt, FaturaVenceu)
        assert evt.dias_atraso >= 0


# --- PagamentoConfirmado emitido em transição →pago ---


class TestPagamentoConfirmadoEvent:
    def test_transicao_para_pago_emite_evento(self):
        agg = _make_aggregate(status="pendente")
        agg.transicionar(FaturaStatus.PAGO)
        events = agg.collect_events()
        assert len(events) == 1
        assert isinstance(events[0], PagamentoConfirmado)

    def test_vencido_para_pago_emite_evento(self):
        agg = _make_aggregate(status="vencido")
        agg.transicionar(FaturaStatus.PAGO)
        events = agg.collect_events()
        assert len(events) == 1
        assert isinstance(events[0], PagamentoConfirmado)

    def test_evento_contem_dados_corretos(self):
        agg = _make_aggregate(
            status="vencido",
            id="fat_abc",
            cliente_id="cli_xyz",
            valor=150000,
        )
        agg.transicionar(FaturaStatus.PAGO)
        evt = agg.collect_events()[0]
        assert isinstance(evt, PagamentoConfirmado)
        assert evt.fatura_id == "fat_abc"
        assert evt.cliente_id == "cli_xyz"
        assert evt.valor_centavos == 150000
        assert evt.meio_pagamento == ""  # Será preenchido pelo service


# --- Transições que NÃO emitem eventos ---


class TestTransicoesSemEvento:
    def test_transicao_para_cancelado_nao_emite_evento(self):
        agg = _make_aggregate(status="pendente")
        agg.transicionar(FaturaStatus.CANCELADO)
        assert agg.collect_events() == []

    def test_transicao_invalida_nao_emite_evento(self):
        agg = _make_aggregate(status="pago")
        with pytest.raises(Exception):
            agg.transicionar(FaturaStatus.PENDENTE)
        assert agg.collect_events() == []
