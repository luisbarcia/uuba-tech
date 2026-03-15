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


@router.post("", response_model=CobrancaResponse, status_code=201)
async def create_cobranca(data: CobrancaCreate, db: AsyncSession = Depends(get_db)):
    return await cobranca_service.create_cobranca(db, data)


@router.get("", response_model=ListResponse)
async def list_cobrancas(
    periodo: str | None = Query(None),
    cliente_id: str | None = Query(None),
    fatura_id: str | None = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    items, total = await cobranca_service.list_cobrancas(
        db, periodo=periodo, cliente_id=cliente_id, fatura_id=fatura_id,
        limit=limit, offset=offset,
    )
    return ListResponse(
        data=[CobrancaResponse.model_validate(c) for c in items],
        pagination=PaginationMeta(
            total=total, page_size=limit, has_more=(offset + limit) < total, offset=offset
        ),
    )


@router.get("/{fatura_id}/historico", response_model=ListResponse)
async def get_historico(fatura_id: str, db: AsyncSession = Depends(get_db)):
    items = await cobranca_service.get_historico(db, fatura_id)
    return ListResponse(
        data=[CobrancaResponse.model_validate(c) for c in items],
        pagination=PaginationMeta(total=len(items), page_size=len(items), has_more=False),
    )


@router.patch("/{cobranca_id}/pausar", response_model=CobrancaResponse)
async def pausar(cobranca_id: str, db: AsyncSession = Depends(get_db)):
    cobranca = await cobranca_service.pausar(db, cobranca_id)
    if not cobranca:
        raise APIError(
            404, "cobranca-nao-encontrada", "Cobrança não encontrada",
            f"Cobrança {cobranca_id} não existe.",
        )
    return cobranca


@router.patch("/{cobranca_id}/retomar", response_model=CobrancaResponse)
async def retomar(cobranca_id: str, db: AsyncSession = Depends(get_db)):
    cobranca = await cobranca_service.retomar(db, cobranca_id)
    if not cobranca:
        raise APIError(
            404, "cobranca-nao-encontrada", "Cobrança não encontrada",
            f"Cobrança {cobranca_id} não existe.",
        )
    return cobranca
