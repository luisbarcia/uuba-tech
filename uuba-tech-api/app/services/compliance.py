"""Engine de compliance para cobrança (CDC + LGPD).

Regras:
- Horário: seg-sex 8h-20h, sáb 8h-14h, dom/feriado nunca
- Frequência: max 1 msg/dia, 3/semana por devedor
"""

from datetime import date, datetime, timedelta, timezone

# Feriados nacionais 2026 (fixos + móveis calculados)
FERIADOS_NACIONAIS_2026: set[date] = {
    date(2026, 1, 1),  # Confraternização Universal
    date(2026, 2, 16),  # Carnaval (segunda)
    date(2026, 2, 17),  # Carnaval (terça)
    date(2026, 4, 3),  # Sexta-feira Santa
    date(2026, 4, 5),  # Páscoa
    date(2026, 4, 21),  # Tiradentes
    date(2026, 5, 1),  # Dia do Trabalho
    date(2026, 6, 4),  # Corpus Christi
    date(2026, 9, 7),  # Independência
    date(2026, 10, 12),  # Nossa Senhora Aparecida
    date(2026, 11, 2),  # Finados
    date(2026, 11, 15),  # Proclamação da República
    date(2026, 12, 25),  # Natal
}

MAX_POR_DIA = 1
MAX_POR_SEMANA = 3


def is_horario_util(dt: datetime) -> bool:
    """Verifica se o horário é permitido para envio de cobrança.

    Seg-Sex: 8h-20h
    Sáb: 8h-14h
    Dom/Feriado: nunca
    """
    if dt.date() in FERIADOS_NACIONAIS_2026:
        return False

    weekday = dt.weekday()  # 0=seg, 6=dom

    if weekday == 6:  # domingo
        return False

    hora = dt.hour

    if weekday == 5:  # sábado: 8h-14h
        return 8 <= hora < 14

    # seg-sex: 8h-20h
    return 8 <= hora < 20


def pode_enviar(
    cobrancas_recentes: list[datetime],
    agora: datetime | None = None,
) -> bool:
    """Verifica se pode enviar mais uma cobrança para este devedor.

    Limites: max 1/dia, 3/semana.

    Args:
        cobrancas_recentes: Timestamps de cobranças enviadas nos últimos 7 dias.
        agora: Timestamp atual (default: now UTC).
    """
    if agora is None:
        agora = datetime.now(timezone.utc)

    hoje = agora.date()
    inicio_semana = hoje - timedelta(days=7)

    enviadas_hoje = sum(1 for c in cobrancas_recentes if c.date() == hoje)
    if enviadas_hoje >= MAX_POR_DIA:
        return False

    enviadas_semana = sum(1 for c in cobrancas_recentes if c.date() > inicio_semana)
    if enviadas_semana >= MAX_POR_SEMANA:
        return False

    return True
