"""Router de tenants — CRUD para multi-tenancy."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.api_key import verify_api_key
from app.database import get_db
from app.exceptions import APIError
from app.schemas.common import ListResponse, PaginationMeta
from app.schemas.tenant import TenantCreate, TenantResponse, TenantUpdate
from app.services import tenant_service

router = APIRouter(
    prefix="/api/v1/tenants",
    tags=["tenants"],
    dependencies=[Depends(verify_api_key)],
)


@router.post(
    "",
    response_model=TenantResponse,
    status_code=201,
    summary="Criar tenant",
    description="Registra um novo tenant na plataforma. "
    "O slug eh gerado automaticamente a partir do nome. "
    "NAO gera API key — isso eh responsabilidade do Unkey (via CLI).",
)
async def create_tenant(data: TenantCreate, db: AsyncSession = Depends(get_db)):
    """Cria novo tenant. Retorna 201."""
    tenant = await tenant_service.create_tenant(db, data)
    return TenantResponse.from_model(tenant)


@router.get(
    "",
    response_model=ListResponse,
    summary="Listar tenants",
    description="Retorna todos os tenants com paginacao.",
)
async def list_tenants(
    limit: int = Query(50, ge=1, le=100, description="Itens por pagina (max 100)"),
    offset: int = Query(0, ge=0, description="Pular N itens"),
    db: AsyncSession = Depends(get_db),
):
    """Lista tenants com paginacao."""
    tenants, total = await tenant_service.list_tenants(db, limit=limit, offset=offset)
    return ListResponse(
        data=[TenantResponse.from_model(t) for t in tenants],
        pagination=PaginationMeta(
            total=total, page_size=limit, has_more=(offset + limit) < total, offset=offset
        ),
    )


@router.get(
    "/{tenant_id}",
    response_model=TenantResponse,
    summary="Buscar tenant",
    description="Retorna os dados de um tenant especifico pelo ID.",
)
async def get_tenant(tenant_id: str, db: AsyncSession = Depends(get_db)):
    """Busca tenant por ID. Retorna 404 se nao existir."""
    tenant = await tenant_service.get_tenant(db, tenant_id)
    if not tenant:
        raise APIError(
            404,
            "tenant-nao-encontrado",
            "Tenant nao encontrado",
            f"Tenant {tenant_id} nao existe.",
        )
    return TenantResponse.from_model(tenant)


@router.patch(
    "/{tenant_id}",
    response_model=TenantResponse,
    summary="Atualizar tenant",
    description="Atualiza parcialmente os dados de um tenant. "
    "Envie apenas os campos que deseja alterar.",
)
async def update_tenant(
    tenant_id: str, data: TenantUpdate, db: AsyncSession = Depends(get_db)
):
    """Atualiza parcialmente um tenant. Retorna 404 se nao existir."""
    tenant = await tenant_service.update_tenant(db, tenant_id, data)
    if not tenant:
        raise APIError(
            404,
            "tenant-nao-encontrado",
            "Tenant nao encontrado",
            f"Tenant {tenant_id} nao existe.",
        )
    return TenantResponse.from_model(tenant)
