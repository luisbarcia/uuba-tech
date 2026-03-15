from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.auth.api_key import verify_api_key
from app.exceptions import APIError
from app.schemas.cliente import ClienteCreate, ClienteUpdate, ClienteResponse, ClienteMetricas
from app.schemas.common import ListResponse, PaginationMeta
from app.services import cliente_service

router = APIRouter(
    prefix="/api/v1/clientes",
    tags=["clientes"],
    dependencies=[Depends(verify_api_key)],
)


@router.post("", response_model=ClienteResponse, status_code=201)
async def create_cliente(data: ClienteCreate, db: AsyncSession = Depends(get_db)):
    return await cliente_service.create_cliente(db, data)


@router.get("", response_model=ListResponse)
async def list_clientes(
    telefone: str | None = Query(None),
    order_by: str | None = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    clientes, total = await cliente_service.list_clientes(
        db, telefone=telefone, order_by=order_by, limit=limit, offset=offset
    )
    return ListResponse(
        data=[ClienteResponse.model_validate(c) for c in clientes],
        pagination=PaginationMeta(
            total=total, page_size=limit, has_more=(offset + limit) < total, offset=offset
        ),
    )


@router.get("/{cliente_id}", response_model=ClienteResponse)
async def get_cliente(cliente_id: str, db: AsyncSession = Depends(get_db)):
    cliente = await cliente_service.get_cliente(db, cliente_id)
    if not cliente:
        raise APIError(
            404, "cliente-nao-encontrado", "Cliente não encontrado",
            f"Cliente {cliente_id} não existe.",
        )
    return cliente


@router.patch("/{cliente_id}", response_model=ClienteResponse)
async def update_cliente(
    cliente_id: str, data: ClienteUpdate, db: AsyncSession = Depends(get_db)
):
    cliente = await cliente_service.update_cliente(db, cliente_id, data)
    if not cliente:
        raise APIError(
            404, "cliente-nao-encontrado", "Cliente não encontrado",
            f"Cliente {cliente_id} não existe.",
        )
    return cliente


@router.get("/{cliente_id}/metricas", response_model=ClienteMetricas)
async def get_metricas(cliente_id: str, db: AsyncSession = Depends(get_db)):
    cliente = await cliente_service.get_cliente(db, cliente_id)
    if not cliente:
        raise APIError(
            404, "cliente-nao-encontrado", "Cliente não encontrado",
            f"Cliente {cliente_id} não existe.",
        )
    return await cliente_service.get_metricas(db, cliente_id)
