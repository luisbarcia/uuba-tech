"""Testes unitários puros de Domain Events.

Sem banco de dados, sem HTTP — testa apenas objetos de domínio.
"""

from datetime import datetime, timezone

import pytest

from app.domain.events.base import DomainEvent
from app.domain.events.fatura_events import (
    CobrancaEnviada,
    EscalacaoSolicitada,
    FaturaVenceu,
    PagamentoConfirmado,
    PromessaRegistrada,
)


# --- DomainEvent base ---


class TestDomainEventBase:
    def test_event_tem_id_com_prefixo_evt(self):
        evt = DomainEvent()
        assert evt.event_id.startswith("evt_")

    def test_event_tem_occurred_at_utc(self):
        evt = DomainEvent()
        assert evt.occurred_at is not None
        assert evt.occurred_at.tzinfo is not None

    def test_event_eh_imutavel(self):
        evt = DomainEvent()
        with pytest.raises(AttributeError):
            evt.event_id = "outro"  # type: ignore[misc]

    def test_dois_events_tem_ids_diferentes(self):
        e1 = DomainEvent()
        e2 = DomainEvent()
        assert e1.event_id != e2.event_id


# --- FaturaVenceu ---


class TestFaturaVenceu:
    def test_campos_obrigatorios(self):
        evt = FaturaVenceu(
            fatura_id="fat_abc",
            cliente_id="cli_xyz",
            valor_centavos=100000,
            dias_atraso=5,
        )
        assert evt.fatura_id == "fat_abc"
        assert evt.cliente_id == "cli_xyz"
        assert evt.valor_centavos == 100000
        assert evt.dias_atraso == 5

    def test_herda_domain_event(self):
        evt = FaturaVenceu(
            fatura_id="fat_abc",
            cliente_id="cli_xyz",
            valor_centavos=100000,
            dias_atraso=5,
        )
        assert isinstance(evt, DomainEvent)
        assert evt.event_id.startswith("evt_")

    def test_eh_imutavel(self):
        evt = FaturaVenceu(
            fatura_id="fat_abc",
            cliente_id="cli_xyz",
            valor_centavos=100000,
            dias_atraso=5,
        )
        with pytest.raises(AttributeError):
            evt.fatura_id = "outro"  # type: ignore[misc]


# --- PagamentoConfirmado ---


class TestPagamentoConfirmado:
    def test_campos_obrigatorios(self):
        evt = PagamentoConfirmado(
            fatura_id="fat_abc",
            cliente_id="cli_xyz",
            valor_centavos=50000,
            meio_pagamento="pix",
        )
        assert evt.fatura_id == "fat_abc"
        assert evt.meio_pagamento == "pix"

    def test_herda_domain_event(self):
        evt = PagamentoConfirmado(
            fatura_id="fat_abc",
            cliente_id="cli_xyz",
            valor_centavos=50000,
            meio_pagamento="pix",
        )
        assert isinstance(evt, DomainEvent)


# --- CobrancaEnviada ---


class TestCobrancaEnviada:
    def test_campos_obrigatorios(self):
        evt = CobrancaEnviada(
            cobranca_id="cob_abc",
            fatura_id="fat_abc",
            cliente_id="cli_xyz",
            canal="whatsapp",
            tom="amigavel",
        )
        assert evt.cobranca_id == "cob_abc"
        assert evt.canal == "whatsapp"
        assert evt.tom == "amigavel"

    def test_herda_domain_event(self):
        evt = CobrancaEnviada(
            cobranca_id="cob_abc",
            fatura_id="fat_abc",
            cliente_id="cli_xyz",
            canal="whatsapp",
            tom="amigavel",
        )
        assert isinstance(evt, DomainEvent)


# --- PromessaRegistrada ---


class TestPromessaRegistrada:
    def test_campos_obrigatorios(self):
        data = datetime(2026, 4, 15, tzinfo=timezone.utc)
        evt = PromessaRegistrada(
            fatura_id="fat_abc",
            cliente_id="cli_xyz",
            data_promessa=data,
        )
        assert evt.data_promessa == data

    def test_herda_domain_event(self):
        evt = PromessaRegistrada(
            fatura_id="fat_abc",
            cliente_id="cli_xyz",
            data_promessa=datetime(2026, 4, 15, tzinfo=timezone.utc),
        )
        assert isinstance(evt, DomainEvent)


# --- EscalacaoSolicitada ---


class TestEscalacaoSolicitada:
    def test_campos_obrigatorios(self):
        evt = EscalacaoSolicitada(
            fatura_id="fat_abc",
            cliente_id="cli_xyz",
            motivo="cliente agressivo",
        )
        assert evt.motivo == "cliente agressivo"

    def test_herda_domain_event(self):
        evt = EscalacaoSolicitada(
            fatura_id="fat_abc",
            cliente_id="cli_xyz",
            motivo="cliente agressivo",
        )
        assert isinstance(evt, DomainEvent)
