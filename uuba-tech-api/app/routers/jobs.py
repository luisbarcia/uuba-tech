from fastapi import APIRouter, Depends

from app.database import get_fatura_repository
from app.auth.api_key import verify_api_key
from app.services import fatura_service

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
    count = await fatura_service.transicionar_faturas_vencidas(repo)
    return {
        "status": "ok",
        "transicionadas": count,
    }
