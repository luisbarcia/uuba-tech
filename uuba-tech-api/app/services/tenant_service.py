"""Servico de tenants.

CRUD de tenants com geracao de ID prefixado e slug automatico.
"""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import APIError
from app.models.tenant import Tenant, _slugify
from app.schemas.tenant import TenantCreate, TenantUpdate
from app.utils.ids import generate_id


async def create_tenant(db: AsyncSession, data: TenantCreate) -> Tenant:
    """Cria um novo tenant com ID prefixado e slug automatico.

    Raises:
        APIError(409): Se slug gerado a partir do nome ja existir.
    """
    from sqlalchemy.exc import IntegrityError

    tenant = Tenant(
        id=generate_id("ten"),
        nome=data.name,
        slug=_slugify(data.name),
        ativo=True,
        plan="starter",
    )
    db.add(tenant)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise APIError(
            409,
            "slug-duplicado",
            "Tenant com este nome ja existe",
            f"O slug '{_slugify(data.name)}' ja esta em uso. Escolha outro nome.",
        )
    await db.refresh(tenant)
    return tenant


async def list_tenants(
    db: AsyncSession,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[Tenant], int]:
    """Lista tenants com paginacao."""
    count_q = select(func.count(Tenant.id))
    total = (await db.execute(count_q)).scalar() or 0

    query = select(Tenant).order_by(Tenant.nome).limit(limit).offset(offset)
    result = await db.execute(query)
    return result.scalars().all(), total


async def get_tenant(db: AsyncSession, tenant_id: str) -> Tenant | None:
    """Busca tenant por ID."""
    result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
    return result.scalar_one_or_none()


async def update_tenant(
    db: AsyncSession, tenant_id: str, data: TenantUpdate
) -> Tenant | None:
    """Atualiza campos do tenant (patch parcial)."""
    result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
    tenant = result.scalar_one_or_none()
    if not tenant:
        return None

    update_data = data.model_dump(exclude_unset=True)

    if "name" in update_data:
        tenant.nome = update_data["name"]
        tenant.slug = _slugify(update_data["name"])
    if "active" in update_data:
        tenant.ativo = update_data["active"]
    if "plan" in update_data:
        tenant.plan = update_data["plan"]

    await db.commit()
    await db.refresh(tenant)
    return tenant
