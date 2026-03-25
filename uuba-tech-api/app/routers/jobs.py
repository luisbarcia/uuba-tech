"""Router de jobs — tarefas agendáveis (transição de vencidas, régua de cobrança)."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.api_key import verify_api_key
from app.database import get_db, get_event_bus, get_fatura_repository
from app.services import fatura_service, regua_service

router = APIRouter(
    prefix="/api/v1/jobs",
    tags=["jobs"],
    dependencies=[Depends(verify_api_key)],
)


@router.post(
    "/transicionar-vencidas",
    summary="Transicionar faturas vencidas",
    description=(
        "Job idempotente que transiciona faturas com status `pendente` e "
        "vencimento ultrapassado para `vencido`. Pode ser chamado por cron "
        "externo ou ARQ worker. Rodar múltiplas vezes no mesmo dia não "
        "causa efeitos colaterais."
    ),
)
async def transicionar_vencidas(repo=Depends(get_fatura_repository)):
    """Transiciona faturas pendentes com vencimento ultrapassado para vencido. Idempotente.

    Args:
        repo: Repositório de faturas (injetado).

    Returns:
        Dict com quantidade de faturas transicionadas.
    """
    count = await fatura_service.transicionar_faturas_vencidas(repo)
    return {
        "status": "ok",
        "transicionadas": count,
    }


@router.post(
    "/processar-regua",
    summary="Processar régua de cobrança",
    description=(
        "Executa um ciclo da régua de cobrança automática. Para cada fatura "
        "vencida, identifica o próximo passo, verifica compliance (horário, "
        "frequência) e registra a cobrança. Idempotente — não repete passos "
        "já executados."
    ),
)
async def processar_regua(
    request: Request,
    db: AsyncSession = Depends(get_db),
    event_bus=Depends(get_event_bus),
    simular_horario: str | None = Query(
        None,
        description="ISO 8601 datetime para simular horário (debug/testes). "
        "Ex: 2026-03-25T10:00:00Z",
    ),
):
    """Executa um ciclo da régua de cobrança automática. Idempotente.

    Args:
        request: Request HTTP (usado para extrair tenant_id).
        db: Sessão assíncrona do banco (injetada).
        event_bus: Barramento de eventos (injetado).
        simular_horario: Datetime ISO 8601 para simular horário em testes.

    Returns:
        Dict com resultado do processamento (cobranças criadas, ignoradas).
    """
    agora = None
    if simular_horario:
        agora = datetime.fromisoformat(simular_horario)
        if agora.tzinfo is None:
            agora = agora.replace(tzinfo=timezone.utc)
    tenant_id = request.state.tenant_id
    return await regua_service.processar_regua(db, tenant_id, event_bus=event_bus, agora=agora)
