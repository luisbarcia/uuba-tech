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


@router.post(
    "",
    response_model=ClienteResponse,
    status_code=201,
    summary="Cadastrar cliente",
    description="Registra um novo cliente na carteira. O campo `documento` (CPF ou CNPJ) deve ser único.",
)
async def create_cliente(data: ClienteCreate, db: AsyncSession = Depends(get_db)):
    return await cliente_service.create_cliente(db, data)


@router.get(
    "",
    response_model=ListResponse,
    summary="Listar clientes",
    description="Retorna a lista de clientes com suporte a filtro por telefone. Use `telefone` para buscar pelo número WhatsApp.",
)
async def list_clientes(
    telefone: str | None = Query(None, description="Filtrar por número WhatsApp (ex: 5511999001234)"),
    order_by: str | None = Query(None, description="Ordenação (ex: total_vencido)"),
    limit: int = Query(50, le=100, description="Itens por página (max 100)"),
    offset: int = Query(0, ge=0, description="Pular N itens"),
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


@router.get(
    "/{cliente_id}",
    response_model=ClienteResponse,
    summary="Buscar cliente",
    description="Retorna os dados de um cliente específico pelo ID.",
)
async def get_cliente(cliente_id: str, db: AsyncSession = Depends(get_db)):
    cliente = await cliente_service.get_cliente(db, cliente_id)
    if not cliente:
        raise APIError(
            404, "cliente-nao-encontrado", "Cliente não encontrado",
            f"Cliente {cliente_id} não existe.",
        )
    return cliente


@router.patch(
    "/{cliente_id}",
    response_model=ClienteResponse,
    summary="Atualizar cliente",
    description="Atualiza parcialmente os dados de um cliente. Envie apenas os campos que deseja alterar.",
)
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


@router.get(
    "/{cliente_id}/metricas",
    response_model=ClienteMetricas,
    summary="Métricas de pagamento",
    description="Retorna indicadores financeiros do cliente: DSO (dias médios para pagamento), total em aberto, total vencido, e contagem de faturas.",
)
async def get_metricas(cliente_id: str, db: AsyncSession = Depends(get_db)):
    cliente = await cliente_service.get_cliente(db, cliente_id)
    if not cliente:
        raise APIError(
            404, "cliente-nao-encontrado", "Cliente não encontrado",
            f"Cliente {cliente_id} não existe.",
        )
    return await cliente_service.get_metricas(db, cliente_id)
