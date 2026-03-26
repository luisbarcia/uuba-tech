"""Router de faturas — CRUD com filtros por status e cliente."""

from fastapi import APIRouter, Depends, Query

from app.database import get_event_bus, get_fatura_repository
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


@router.post(
    "",
    response_model=FaturaResponse,
    status_code=201,
    summary="Registrar fatura",
    description="Cria uma nova fatura a receber vinculada a um cliente. O valor deve ser em centavos (R$ 2.500,00 = `250000`).",
)
async def create_fatura(data: FaturaCreate, repo=Depends(get_fatura_repository)):
    """Cria nova fatura vinculada a um cliente. Retorna 201.

    Args:
        data: Dados da fatura (valor em centavos).
        repo: Repositório de faturas (injetado).

    Returns:
        FaturaResponse com os dados da fatura criada.
    """
    return await fatura_service.create_fatura(repo, data)


@router.get(
    "",
    response_model=ListResponse,
    summary="Listar faturas",
    description="Retorna faturas com filtros opcionais por status e cliente. Use `status=pendente,vencido` para faturas em aberto.",
)
async def list_faturas(
    status: str | None = Query(
        None,
        description="Filtrar por status (aceita múltiplos separados por vírgula: pendente,vencido)",
    ),
    cliente_id: str | None = Query(None, description="Filtrar por cliente"),
    tenant_id: str | None = Query(None, description="Filtrar por tenant"),
    limit: int = Query(50, ge=1, le=100, description="Itens por página (max 100)"),
    offset: int = Query(0, ge=0, description="Pular N itens"),
    repo=Depends(get_fatura_repository),
):
    """Lista faturas com paginação e filtros por status, cliente e tenant.

    Args:
        status: Status para filtrar, separados por vírgula (opcional).
        cliente_id: ID do cliente para filtrar (opcional).
        tenant_id: ID do tenant para filtrar (opcional, admin).
        limit: Quantidade máxima de itens por página.
        offset: Deslocamento para paginação.
        repo: Repositório de faturas (injetado).

    Returns:
        ListResponse com dados paginados das faturas.
    """
    faturas, total = await fatura_service.list_faturas(
        repo, status=status, cliente_id=cliente_id, limit=limit, offset=offset
    )
    return ListResponse(
        data=[FaturaResponse.model_validate(f) for f in faturas],
        pagination=PaginationMeta(
            total=total, page_size=limit, has_more=(offset + limit) < total, offset=offset
        ),
    )


@router.get(
    "/{fatura_id}",
    response_model=FaturaResponse,
    summary="Buscar fatura",
    description="Retorna os dados completos de uma fatura pelo ID.",
)
async def get_fatura(fatura_id: str, repo=Depends(get_fatura_repository)):
    """Busca fatura por ID. Retorna 404 se não existir.

    Args:
        fatura_id: Identificador único da fatura.
        repo: Repositório de faturas (injetado).

    Returns:
        FaturaResponse com os dados da fatura.
    """
    fatura = await fatura_service.get_fatura(repo, fatura_id)
    if not fatura:
        raise APIError(
            404,
            "fatura-nao-encontrada",
            "Fatura não encontrada",
            f"Fatura {fatura_id} não existe.",
        )
    return fatura


@router.patch(
    "/{fatura_id}",
    response_model=FaturaResponse,
    summary="Atualizar fatura",
    description="Atualiza status, promessa de pagamento, ou link de pagamento. Ao marcar como `pago`, o campo `pago_em` é preenchido automaticamente.",
)
async def update_fatura(
    fatura_id: str,
    data: FaturaUpdate,
    repo=Depends(get_fatura_repository),
    event_bus=Depends(get_event_bus),
):
    """Atualiza status ou dados de uma fatura. Retorna 404 se não existir.

    Args:
        fatura_id: Identificador único da fatura.
        data: Campos a atualizar (parcial).
        repo: Repositório de faturas (injetado).
        event_bus: Barramento de eventos (injetado).

    Returns:
        FaturaResponse com os dados atualizados.
    """
    fatura = await fatura_service.update_fatura(repo, fatura_id, data, event_bus=event_bus)
    if not fatura:
        raise APIError(
            404,
            "fatura-nao-encontrada",
            "Fatura não encontrada",
            f"Fatura {fatura_id} não existe.",
        )
    return fatura
