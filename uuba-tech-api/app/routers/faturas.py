from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.auth.api_key import verify_api_key
from app.exceptions import APIError
from app.schemas.fatura import FaturaCreate, FaturaUpdate, FaturaResponse
from app.schemas.common import ListResponse, PaginationMeta
from app.services import fatura_service

router = APIRouter(
    prefix="/api/v1/faturas",
    tags=["faturas"],
    dependencies=[Depends(verify_api_key)],
)


@router.post("", response_model=FaturaResponse, status_code=201)
async def create_fatura(data: FaturaCreate, db: AsyncSession = Depends(get_db)):
    return await fatura_service.create_fatura(db, data)


@router.get("", response_model=ListResponse)
async def list_faturas(
    status: str | None = Query(None),
    cliente_id: str | None = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    faturas, total = await fatura_service.list_faturas(
        db, status=status, cliente_id=cliente_id, limit=limit, offset=offset
    )
    return ListResponse(
        data=[FaturaResponse.model_validate(f) for f in faturas],
        pagination=PaginationMeta(
            total=total, page_size=limit, has_more=(offset + limit) < total, offset=offset
        ),
    )


@router.get("/{fatura_id}", response_model=FaturaResponse)
async def get_fatura(fatura_id: str, db: AsyncSession = Depends(get_db)):
    fatura = await fatura_service.get_fatura(db, fatura_id)
    if not fatura:
        raise APIError(
            404, "fatura-nao-encontrada", "Fatura não encontrada",
            f"Fatura {fatura_id} não existe.",
        )
    return fatura


@router.patch("/{fatura_id}", response_model=FaturaResponse)
async def update_fatura(
    fatura_id: str, data: FaturaUpdate, db: AsyncSession = Depends(get_db)
):
    fatura = await fatura_service.update_fatura(db, fatura_id, data)
    if not fatura:
        raise APIError(
            404, "fatura-nao-encontrada", "Fatura não encontrada",
            f"Fatura {fatura_id} não existe.",
        )
    return fatura
