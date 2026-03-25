"""Testes do engine de compliance da régua de cobrança.

Horários permitidos, limites de frequência, feriados.
"""

from datetime import datetime, timezone

from app.services.compliance import (
    FERIADOS_NACIONAIS_2026,
    is_horario_util,
    pode_enviar,
)


# --- Horário útil ---


class TestHorarioUtil:
    def test_segunda_10h_permitido(self):
        dt = datetime(2026, 3, 23, 10, 0, tzinfo=timezone.utc)  # seg
        assert is_horario_util(dt) is True

    def test_segunda_7h_bloqueado(self):
        dt = datetime(2026, 3, 23, 7, 0, tzinfo=timezone.utc)  # seg 7h
        assert is_horario_util(dt) is False

    def test_segunda_20h_bloqueado(self):
        dt = datetime(2026, 3, 23, 20, 0, tzinfo=timezone.utc)  # seg 20h
        assert is_horario_util(dt) is False

    def test_segunda_19h59_permitido(self):
        dt = datetime(2026, 3, 23, 19, 59, tzinfo=timezone.utc)
        assert is_horario_util(dt) is True

    def test_sabado_10h_permitido(self):
        dt = datetime(2026, 3, 28, 10, 0, tzinfo=timezone.utc)  # sáb
        assert is_horario_util(dt) is True

    def test_sabado_14h_bloqueado(self):
        dt = datetime(2026, 3, 28, 14, 0, tzinfo=timezone.utc)  # sáb 14h
        assert is_horario_util(dt) is False

    def test_domingo_10h_bloqueado(self):
        dt = datetime(2026, 3, 29, 10, 0, tzinfo=timezone.utc)  # dom
        assert is_horario_util(dt) is False

    def test_feriado_bloqueado(self):
        # 1 de janeiro (Confraternização Universal)
        dt = datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc)
        assert is_horario_util(dt) is False

    def test_sexta_19h_permitido(self):
        dt = datetime(2026, 3, 27, 19, 0, tzinfo=timezone.utc)  # sex
        assert is_horario_util(dt) is True


# --- Frequência por devedor ---


class TestPodeEnviar:
    def test_sem_cobrancas_pode_enviar(self):
        assert pode_enviar(cobrancas_recentes=[]) is True

    def test_1_cobranca_hoje_bloqueia(self):
        hoje = datetime(2026, 3, 25, 10, 0, tzinfo=timezone.utc)
        cobrancas = [hoje]
        assert pode_enviar(cobrancas_recentes=cobrancas, agora=hoje) is False

    def test_1_cobranca_ontem_permite(self):
        agora = datetime(2026, 3, 25, 10, 0, tzinfo=timezone.utc)
        cobrancas = [datetime(2026, 3, 24, 10, 0, tzinfo=timezone.utc)]
        assert pode_enviar(cobrancas_recentes=cobrancas, agora=agora) is True

    def test_3_cobrancas_na_semana_bloqueia(self):
        agora = datetime(2026, 3, 27, 10, 0, tzinfo=timezone.utc)  # sex
        cobrancas = [
            datetime(2026, 3, 23, 10, 0, tzinfo=timezone.utc),  # seg
            datetime(2026, 3, 24, 10, 0, tzinfo=timezone.utc),  # ter
            datetime(2026, 3, 25, 10, 0, tzinfo=timezone.utc),  # qua
        ]
        assert pode_enviar(cobrancas_recentes=cobrancas, agora=agora) is False

    def test_2_cobrancas_na_semana_permite(self):
        agora = datetime(2026, 3, 27, 10, 0, tzinfo=timezone.utc)
        cobrancas = [
            datetime(2026, 3, 23, 10, 0, tzinfo=timezone.utc),
            datetime(2026, 3, 25, 10, 0, tzinfo=timezone.utc),
        ]
        assert pode_enviar(cobrancas_recentes=cobrancas, agora=agora) is True


# --- Feriados ---


class TestFeriados:
    def test_lista_feriados_2026_tem_pelo_menos_10(self):
        assert len(FERIADOS_NACIONAIS_2026) >= 10

    def test_natal_eh_feriado(self):
        from datetime import date

        assert date(2026, 12, 25) in FERIADOS_NACIONAIS_2026

    def test_dia_normal_nao_eh_feriado(self):
        from datetime import date

        assert date(2026, 3, 25) not in FERIADOS_NACIONAIS_2026
