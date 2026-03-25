"""Testes de edge cases do compliance engine.

Fronteiras de horário, múltiplos devedores, template sem dados opcionais.
"""

from datetime import datetime, timezone

from app.services.compliance import is_horario_util, pode_enviar
from app.services.regua_service import _proximo_passo, _renderizar_template


# --- Fronteiras exatas de horário ---


class TestFronteirasHorario:
    def test_seg_7h59_bloqueado(self):
        dt = datetime(2026, 3, 23, 7, 59, tzinfo=timezone.utc)
        assert is_horario_util(dt) is False

    def test_seg_8h00_permitido(self):
        dt = datetime(2026, 3, 23, 8, 0, tzinfo=timezone.utc)
        assert is_horario_util(dt) is True

    def test_seg_19h59_permitido(self):
        dt = datetime(2026, 3, 23, 19, 59, tzinfo=timezone.utc)
        assert is_horario_util(dt) is True

    def test_seg_20h00_bloqueado(self):
        dt = datetime(2026, 3, 23, 20, 0, tzinfo=timezone.utc)
        assert is_horario_util(dt) is False

    def test_sab_7h59_bloqueado(self):
        dt = datetime(2026, 3, 28, 7, 59, tzinfo=timezone.utc)
        assert is_horario_util(dt) is False

    def test_sab_8h00_permitido(self):
        dt = datetime(2026, 3, 28, 8, 0, tzinfo=timezone.utc)
        assert is_horario_util(dt) is True

    def test_sab_13h59_permitido(self):
        dt = datetime(2026, 3, 28, 13, 59, tzinfo=timezone.utc)
        assert is_horario_util(dt) is True

    def test_sab_14h00_bloqueado(self):
        dt = datetime(2026, 3, 28, 14, 0, tzinfo=timezone.utc)
        assert is_horario_util(dt) is False


# --- Frequência: edge cases ---


class TestFrequenciaEdgeCases:
    def test_cobranca_exatamente_7_dias_atras_nao_conta(self):
        """Cobrança de exatamente 7 dias atrás não deve contar na semana."""
        agora = datetime(2026, 3, 27, 10, 0, tzinfo=timezone.utc)
        cobrancas = [datetime(2026, 3, 20, 10, 0, tzinfo=timezone.utc)]  # 7 dias
        assert pode_enviar(cobrancas_recentes=cobrancas, agora=agora) is True

    def test_cobranca_6_dias_atras_conta(self):
        """Cobrança de 6 dias atrás ainda conta na semana."""
        agora = datetime(2026, 3, 27, 10, 0, tzinfo=timezone.utc)
        cobrancas = [
            datetime(2026, 3, 21, 10, 0, tzinfo=timezone.utc),
            datetime(2026, 3, 23, 10, 0, tzinfo=timezone.utc),
            datetime(2026, 3, 25, 10, 0, tzinfo=timezone.utc),
        ]
        assert pode_enviar(cobrancas_recentes=cobrancas, agora=agora) is False

    def test_cobranca_meia_noite_hoje(self):
        """Cobrança à 00:01 do mesmo dia bloqueia nova cobrança às 10h."""
        agora = datetime(2026, 3, 25, 10, 0, tzinfo=timezone.utc)
        cobrancas = [datetime(2026, 3, 25, 0, 1, tzinfo=timezone.utc)]
        assert pode_enviar(cobrancas_recentes=cobrancas, agora=agora) is False

    def test_cobranca_23h59_ontem_permite_hoje(self):
        """Cobrança às 23:59 de ontem permite nova cobrança hoje."""
        agora = datetime(2026, 3, 25, 10, 0, tzinfo=timezone.utc)
        cobrancas = [datetime(2026, 3, 24, 23, 59, tzinfo=timezone.utc)]
        assert pode_enviar(cobrancas_recentes=cobrancas, agora=agora) is True

    def test_lista_vazia_sempre_permite(self):
        assert pode_enviar(cobrancas_recentes=[]) is True

    def test_lista_com_muitas_cobrancas_antigas(self):
        """Cobranças de >7 dias atrás não bloqueiam."""
        agora = datetime(2026, 3, 27, 10, 0, tzinfo=timezone.utc)
        cobrancas = [
            datetime(2026, 3, 1, 10, 0, tzinfo=timezone.utc),
            datetime(2026, 3, 5, 10, 0, tzinfo=timezone.utc),
            datetime(2026, 3, 10, 10, 0, tzinfo=timezone.utc),
            datetime(2026, 3, 15, 10, 0, tzinfo=timezone.utc),
        ]
        assert pode_enviar(cobrancas_recentes=cobrancas, agora=agora) is True


# --- Seleção de passo da régua ---


class TestProximoPasso:
    def test_fatura_d0_nenhum_passo(self):
        """Fatura vencida hoje (D+0): nenhum passo aplicável (primeiro é D+1)."""

        class FakePasso:
            def __init__(self, dias):
                self.dias_atraso = dias

        passos = [FakePasso(1), FakePasso(3), FakePasso(7)]
        assert _proximo_passo(passos, dias_atraso=0) is None

    def test_fatura_d1_retorna_primeiro_passo(self):
        class FakePasso:
            def __init__(self, dias):
                self.dias_atraso = dias

        passos = [FakePasso(1), FakePasso(3), FakePasso(7)]
        result = _proximo_passo(passos, dias_atraso=1)
        assert result.dias_atraso == 1

    def test_fatura_d5_retorna_d3(self):
        """D+5: passo D+3 é o mais avançado aplicável."""

        class FakePasso:
            def __init__(self, dias):
                self.dias_atraso = dias

        passos = [FakePasso(1), FakePasso(3), FakePasso(7)]
        result = _proximo_passo(passos, dias_atraso=5)
        assert result.dias_atraso == 3

    def test_fatura_d100_retorna_ultimo_passo(self):
        """Fatura com 100 dias de atraso: retorna último passo da régua."""

        class FakePasso:
            def __init__(self, dias):
                self.dias_atraso = dias

        passos = [FakePasso(1), FakePasso(3), FakePasso(7), FakePasso(15)]
        result = _proximo_passo(passos, dias_atraso=100)
        assert result.dias_atraso == 15

    def test_lista_vazia(self):
        assert _proximo_passo([], dias_atraso=5) is None


# --- Renderização de template com dados faltantes ---


class TestRenderizarTemplate:
    def test_fatura_sem_numero_nf(self):
        class FakeFatura:
            numero_nf = None
            valor = 250000
            vencimento = datetime(2026, 3, 10, tzinfo=timezone.utc)
            pagamento_link = None

        msg = _renderizar_template(
            "Fatura {numero_nf} - R$ {valor} - {link_pagamento}",
            FakeFatura(),
            dias_atraso=15,
        )
        assert "S/N" in msg
        assert "(link pendente)" in msg
        assert "2.500,00" in msg

    def test_valor_zero(self):
        class FakeFatura:
            numero_nf = "NF-001"
            valor = 0
            vencimento = datetime(2026, 3, 10, tzinfo=timezone.utc)
            pagamento_link = "https://pag.test/x"

        msg = _renderizar_template("{valor}", FakeFatura(), dias_atraso=0)
        assert "0,00" in msg

    def test_valor_centavos(self):
        class FakeFatura:
            numero_nf = "NF-001"
            valor = 99
            vencimento = datetime(2026, 3, 10, tzinfo=timezone.utc)
            pagamento_link = None

        msg = _renderizar_template("R$ {valor}", FakeFatura(), dias_atraso=1)
        assert "0,99" in msg
