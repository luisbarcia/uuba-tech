"""Testes unitários puros do FaturaAggregate.

Sem banco de dados, sem HTTP — testa apenas lógica de domínio.
"""

from datetime import datetime, timezone

import pytest

from app.domain.aggregates.fatura import CobrancaData, FaturaAggregate
from app.domain.value_objects.cobranca_enums import CobrancaStatus
from app.domain.value_objects.fatura_status import FaturaStatus
from app.exceptions import APIError


def _make_aggregate(status: str = "pendente", **overrides) -> FaturaAggregate:
    """Helper para criar aggregate com defaults sensatos."""
    defaults = dict(
        id="fat_test1",
        cliente_id="cli_test1",
        valor=100000,
        moeda="BRL",
        status=status,
        vencimento=datetime(2026, 4, 1, tzinfo=timezone.utc),
        descricao=None,
        numero_nf=None,
        pagamento_link=None,
        pago_em=None,
        promessa_pagamento=None,
    )
    defaults.update(overrides)
    return FaturaAggregate.from_primitives(**defaults)


def _make_cobranca(id: str = "cob_test1", **overrides) -> CobrancaData:
    """Helper para criar CobrancaData."""
    defaults = dict(
        id=id,
        fatura_id="fat_test1",
        cliente_id="cli_test1",
        tipo="lembrete",
        canal="whatsapp",
        mensagem=None,
        tom="amigavel",
        status="enviado",
        pausado=False,
        agent_decision_id=None,
        enviado_em=datetime.now(timezone.utc),
    )
    defaults.update(overrides)
    return CobrancaData(**defaults)


# --- from_primitives ---


class TestFromPrimitives:
    def test_cria_aggregate_com_status_enum(self):
        agg = _make_aggregate(status="pendente")
        assert agg.status == FaturaStatus.PENDENTE

    def test_cria_aggregate_com_cobrancas(self):
        cob_dict = dict(
            id="cob_1",
            fatura_id="fat_test1",
            cliente_id="cli_test1",
            tipo="lembrete",
            canal="whatsapp",
            mensagem=None,
            tom=None,
            status="enviado",
            pausado=False,
            agent_decision_id=None,
            enviado_em=None,
        )
        agg = _make_aggregate(cobrancas=[cob_dict])
        assert len(agg.cobrancas) == 1
        assert agg.cobrancas[0].id == "cob_1"

    def test_cria_aggregate_sem_cobrancas(self):
        agg = _make_aggregate()
        assert agg.cobrancas == []


# --- Transições de status ---


class TestTransicao:
    def test_pendente_para_pago(self):
        agg = _make_aggregate(status="pendente")
        agg.transicionar(FaturaStatus.PAGO)
        assert agg.status == FaturaStatus.PAGO

    def test_pendente_para_vencido(self):
        agg = _make_aggregate(status="pendente")
        agg.transicionar(FaturaStatus.VENCIDO)
        assert agg.status == FaturaStatus.VENCIDO

    def test_pendente_para_cancelado(self):
        agg = _make_aggregate(status="pendente")
        agg.transicionar(FaturaStatus.CANCELADO)
        assert agg.status == FaturaStatus.CANCELADO

    def test_vencido_para_pago(self):
        agg = _make_aggregate(status="vencido")
        agg.transicionar(FaturaStatus.PAGO)
        assert agg.status == FaturaStatus.PAGO

    def test_vencido_para_cancelado(self):
        agg = _make_aggregate(status="vencido")
        agg.transicionar(FaturaStatus.CANCELADO)
        assert agg.status == FaturaStatus.CANCELADO

    def test_pago_para_qualquer_levanta_erro(self):
        agg = _make_aggregate(status="pago")
        for target in [FaturaStatus.PENDENTE, FaturaStatus.VENCIDO, FaturaStatus.CANCELADO]:
            with pytest.raises(APIError) as exc_info:
                agg.transicionar(target)
            assert exc_info.value.status == 409
            assert exc_info.value.error_type == "transicao-invalida"

    def test_cancelado_para_qualquer_levanta_erro(self):
        agg = _make_aggregate(status="cancelado")
        for target in [FaturaStatus.PENDENTE, FaturaStatus.VENCIDO, FaturaStatus.PAGO]:
            with pytest.raises(APIError) as exc_info:
                agg.transicionar(target)
            assert exc_info.value.status == 409

    def test_pago_em_preenchido_ao_transicionar_para_pago(self):
        agg = _make_aggregate(status="pendente")
        assert agg.pago_em is None
        agg.transicionar(FaturaStatus.PAGO)
        assert agg.pago_em is not None
        assert agg.pago_em.tzinfo is not None  # timezone-aware

    def test_pago_em_nao_preenchido_para_outros_status(self):
        agg = _make_aggregate(status="pendente")
        agg.transicionar(FaturaStatus.VENCIDO)
        assert agg.pago_em is None


# --- is_terminal ---


class TestIsTerminal:
    def test_pendente_nao_terminal(self):
        assert not _make_aggregate(status="pendente").is_terminal

    def test_vencido_nao_terminal(self):
        assert not _make_aggregate(status="vencido").is_terminal

    def test_pago_terminal(self):
        assert _make_aggregate(status="pago").is_terminal

    def test_cancelado_terminal(self):
        assert _make_aggregate(status="cancelado").is_terminal


# --- Cobranças: adicionar ---


class TestAdicionarCobranca:
    def test_adicionar_em_fatura_pendente(self):
        agg = _make_aggregate(status="pendente")
        cob = _make_cobranca()
        agg.adicionar_cobranca(cob)
        assert len(agg.cobrancas) == 1

    def test_adicionar_em_fatura_vencida(self):
        agg = _make_aggregate(status="vencido")
        cob = _make_cobranca()
        agg.adicionar_cobranca(cob)
        assert len(agg.cobrancas) == 1

    def test_adicionar_em_fatura_paga_levanta_erro(self):
        agg = _make_aggregate(status="pago")
        cob = _make_cobranca()
        with pytest.raises(APIError) as exc_info:
            agg.adicionar_cobranca(cob)
        assert exc_info.value.status == 409
        assert "não aceita novas cobranças" in exc_info.value.detail

    def test_adicionar_em_fatura_cancelada_levanta_erro(self):
        agg = _make_aggregate(status="cancelado")
        cob = _make_cobranca()
        with pytest.raises(APIError) as exc_info:
            agg.adicionar_cobranca(cob)
        assert exc_info.value.status == 409


# --- Cobranças: pausar ---


class TestPausarCobranca:
    def test_pausar_cobranca_existente(self):
        cob = _make_cobranca(id="cob_1")
        agg = _make_aggregate(status="pendente")
        agg.cobrancas.append(cob)

        result = agg.pausar_cobranca("cob_1")
        assert result.pausado is True
        assert result.status == CobrancaStatus.PAUSADO.value

    def test_pausar_cobranca_inexistente_levanta_erro(self):
        agg = _make_aggregate(status="pendente")
        with pytest.raises(APIError) as exc_info:
            agg.pausar_cobranca("cob_nao_existe")
        assert exc_info.value.status == 404


# --- Cobranças: retomar ---


class TestRetomarCobranca:
    def test_retomar_cobranca_fatura_ativa(self):
        cob = _make_cobranca(id="cob_1", pausado=True, status="pausado")
        agg = _make_aggregate(status="pendente")
        agg.cobrancas.append(cob)

        result = agg.retomar_cobranca("cob_1")
        assert result.pausado is False
        assert result.status == CobrancaStatus.ENVIADO.value

    def test_retomar_cobranca_fatura_terminal_levanta_erro(self):
        cob = _make_cobranca(id="cob_1", pausado=True, status="pausado")
        agg = _make_aggregate(status="pago")
        agg.cobrancas.append(cob)

        with pytest.raises(APIError) as exc_info:
            agg.retomar_cobranca("cob_1")
        assert exc_info.value.status == 409

    def test_retomar_cobranca_inexistente_levanta_erro(self):
        agg = _make_aggregate(status="pendente")
        with pytest.raises(APIError) as exc_info:
            agg.retomar_cobranca("cob_nao_existe")
        assert exc_info.value.status == 404


# --- pode_receber_cobranca ---


class TestPodeReceberCobranca:
    def test_pendente_pode(self):
        assert _make_aggregate(status="pendente").pode_receber_cobranca()

    def test_vencido_pode(self):
        assert _make_aggregate(status="vencido").pode_receber_cobranca()

    def test_pago_nao_pode(self):
        assert not _make_aggregate(status="pago").pode_receber_cobranca()

    def test_cancelado_nao_pode(self):
        assert not _make_aggregate(status="cancelado").pode_receber_cobranca()
