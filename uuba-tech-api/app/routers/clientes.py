from fastapi import APIRouter, Depends, Query, Response

from app.auth.api_key import verify_api_key
from app.database import get_cliente_repository, get_cobranca_repository, get_fatura_repository
from app.exceptions import APIError
from app.schemas.cliente import (
    ClienteCreate,
    ClienteListItem,
    ClienteMetricas,
    ClienteResponse,
    ClienteUpdate,
)
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
async def create_cliente(data: ClienteCreate, repo=Depends(get_cliente_repository)):
    return await cliente_service.create_cliente(repo, data)


@router.get(
    "",
    response_model=ListResponse,
    summary="Listar clientes",
    description="Retorna a lista de clientes com suporte a filtro por telefone. Use `telefone` para buscar pelo número WhatsApp.",
)
async def list_clientes(
    telefone: str | None = Query(
        None, description="Filtrar por número WhatsApp (ex: 5511999001234)"
    ),
    limit: int = Query(50, ge=1, le=100, description="Itens por página (max 100)"),
    offset: int = Query(0, ge=0, description="Pular N itens"),
    repo=Depends(get_cliente_repository),
):
    clientes, total = await cliente_service.list_clientes(
        repo, telefone=telefone, limit=limit, offset=offset
    )
    return ListResponse(
        data=[ClienteListItem.from_cliente(c) for c in clientes],
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
async def get_cliente(cliente_id: str, repo=Depends(get_cliente_repository)):
    cliente = await cliente_service.get_cliente(repo, cliente_id)
    if not cliente:
        raise APIError(
            404,
            "cliente-nao-encontrado",
            "Cliente não encontrado",
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
    cliente_id: str, data: ClienteUpdate, repo=Depends(get_cliente_repository)
):
    cliente = await cliente_service.update_cliente(repo, cliente_id, data)
    if not cliente:
        raise APIError(
            404,
            "cliente-nao-encontrado",
            "Cliente não encontrado",
            f"Cliente {cliente_id} não existe.",
        )
    return cliente


@router.delete(
    "/{cliente_id}",
    status_code=204,
    summary="Anonimizar cliente (LGPD)",
    description="Anonimiza dados pessoais do cliente conforme Art. 18 VI da LGPD. "
    "Nome, documento, email e telefone são removidos. Faturas e cobranças "
    "mantêm integridade referencial mas mensagens são apagadas.",
)
async def delete_cliente(cliente_id: str, repo=Depends(get_cliente_repository)):
    anonimizado = await cliente_service.anonimizar_cliente(repo, cliente_id)
    if not anonimizado:
        raise APIError(
            404,
            "cliente-nao-encontrado",
            "Cliente não encontrado",
            f"Cliente {cliente_id} não existe.",
        )
    return Response(status_code=204)


@router.get(
    "/{cliente_id}/metricas",
    response_model=ClienteMetricas,
    summary="Métricas de pagamento",
    description="Retorna indicadores financeiros do cliente: DSO (dias médios para pagamento), total em aberto, total vencido, e contagem de faturas.",
)
async def get_metricas(
    cliente_id: str,
    cliente_repo=Depends(get_cliente_repository),
    fatura_repo=Depends(get_fatura_repository),
):
    cliente = await cliente_service.get_cliente(cliente_repo, cliente_id)
    if not cliente:
        raise APIError(
            404,
            "cliente-nao-encontrado",
            "Cliente não encontrado",
            f"Cliente {cliente_id} não existe.",
        )
    return await cliente_service.get_metricas(fatura_repo, cliente_id)


@router.get(
    "/{cliente_id}/dados-pessoais",
    summary="Dados pessoais do titular (LGPD Art. 18)",
    description="Retorna todos os dados pessoais do titular em formato portável (JSON). "
    "Inclui cadastro, faturas e cobranças associadas. Conforme Art. 18, II e V da LGPD.",
)
async def get_dados_pessoais(
    cliente_id: str,
    cliente_repo=Depends(get_cliente_repository),
    fatura_repo=Depends(get_fatura_repository),
    cobranca_repo=Depends(get_cobranca_repository),
):
    cliente = await cliente_service.get_cliente(cliente_repo, cliente_id)
    if not cliente:
        raise APIError(
            404,
            "cliente-nao-encontrado",
            "Cliente não encontrado",
            f"Cliente {cliente_id} não existe.",
        )
    return await cliente_service.exportar_dados_pessoais(cliente, fatura_repo, cobranca_repo)
