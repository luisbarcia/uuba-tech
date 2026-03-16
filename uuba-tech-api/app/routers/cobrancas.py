from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.auth.api_key import verify_api_key
from app.exceptions import APIError
from app.schemas.cobranca import CobrancaCreate, CobrancaResponse
from app.schemas.common import ListResponse, PaginationMeta
from app.services import cobranca_service

router = APIRouter(
    prefix="/api/v1/cobrancas",
    tags=["cobrancas"],
    dependencies=[Depends(verify_api_key)],
)


@router.post(
    "",
    response_model=CobrancaResponse,
    status_code=201,
    summary="Registrar cobrança",
    description="Registra uma ação de cobrança vinculada a uma fatura. Especifique o tipo (lembrete, cobrança, follow_up, escalação) e opcionalmente o tom e mensagem.",
)
async def create_cobranca(data: CobrancaCreate, db: AsyncSession = Depends(get_db)):
    return await cobranca_service.create_cobranca(db, data)


@router.get(
    "",
    response_model=ListResponse,
    summary="Listar cobranças",
    description="Retorna cobranças com filtros por período, cliente, ou fatura. Use `periodo=7d` para cobranças dos últimos 7 dias.",
)
async def list_cobrancas(
    periodo: str | None = Query(None, description="Período em dias (ex: 7d, 30d)"),
    cliente_id: str | None = Query(None, description="Filtrar por cliente"),
    fatura_id: str | None = Query(None, description="Filtrar por fatura"),
    limit: int = Query(50, ge=1, le=100, description="Itens por página (max 100)"),
    offset: int = Query(0, ge=0, description="Pular N itens"),
    db: AsyncSession = Depends(get_db),
):
    items, total = await cobranca_service.list_cobrancas(
        db,
        periodo=periodo,
        cliente_id=cliente_id,
        fatura_id=fatura_id,
        limit=limit,
        offset=offset,
    )
    return ListResponse(
        data=[CobrancaResponse.model_validate(c) for c in items],
        pagination=PaginationMeta(
            total=total, page_size=limit, has_more=(offset + limit) < total, offset=offset
        ),
    )


@router.get(
    "/{fatura_id}/historico",
    response_model=ListResponse,
    summary="Histórico de cobranças",
    description="Retorna toda a timeline de cobranças enviadas para uma fatura específica, ordenadas da mais recente para a mais antiga.",
)
async def get_historico(fatura_id: str, db: AsyncSession = Depends(get_db)):
    items = await cobranca_service.get_historico(db, fatura_id)
    return ListResponse(
        data=[CobrancaResponse.model_validate(c) for c in items],
        pagination=PaginationMeta(total=len(items), page_size=len(items), has_more=False),
    )


@router.patch(
    "/{cobranca_id}/pausar",
    response_model=CobrancaResponse,
    summary="Pausar cobrança",
    description="Pausa a régua de cobrança para esta fatura. Nenhuma mensagem será enviada enquanto estiver pausada.",
)
async def pausar(cobranca_id: str, db: AsyncSession = Depends(get_db)):
    cobranca = await cobranca_service.pausar(db, cobranca_id)
    if not cobranca:
        raise APIError(
            404,
            "cobranca-nao-encontrada",
            "Cobrança não encontrada",
            f"Cobrança {cobranca_id} não existe.",
        )
    return cobranca


@router.patch(
    "/{cobranca_id}/retomar",
    response_model=CobrancaResponse,
    summary="Retomar cobrança",
    description="Retoma uma cobrança que estava pausada. A régua volta a funcionar normalmente.",
)
async def retomar(cobranca_id: str, db: AsyncSession = Depends(get_db)):
    cobranca = await cobranca_service.retomar(db, cobranca_id)
    if not cobranca:
        raise APIError(
            404,
            "cobranca-nao-encontrada",
            "Cobrança não encontrada",
            f"Cobrança {cobranca_id} não existe.",
        )
    return cobranca
