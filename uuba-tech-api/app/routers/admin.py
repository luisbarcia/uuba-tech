"""Router admin — seed, reset, cleanup LGPD, auditoria e régua de cobrança."""

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.api_key import verify_api_key
from app.config import settings
from app.database import get_db
from app.exceptions import APIError
from app.models.cliente import Cliente
from app.models.cobranca import Cobranca
from app.models.fatura import Fatura
from app.schemas.common import ListResponse, PaginationMeta
from app.models.regua import Regua, ReguaPasso
from app.seed import build_seed_data
from app.seed_regua import build_regua_seed
from app.services import audit_service, cleanup_service

router = APIRouter(
    prefix="/api/v1/admin",
    tags=["admin"],
    dependencies=[Depends(verify_api_key)],
)


def _check_not_production():
    """Bloqueia execução em ambiente de produção. Levanta APIError 403."""
    if settings.environment == "production":
        raise APIError(
            status=403,
            error_type="admin-bloqueado",
            title="Operação bloqueada em produção",
            detail="Endpoints admin estão desabilitados em ambiente de produção.",
        )


@router.post(
    "/seed",
    summary="Popular com dados mock",
    description="Limpa todos os dados e popula com dados mock realistas para demo. **Cuidado: apaga tudo antes de inserir.** Bloqueado em produção.",
)
async def seed_database(db: AsyncSession = Depends(get_db)):
    """Limpa todos os dados e popula com dados mock. Bloqueado em produção.

    Args:
        db: Sessão assíncrona do banco (injetada).

    Returns:
        Dict com contagem de registros inseridos por entidade.
    """
    _check_not_production()
    # Limpar na ordem correta (FK constraints)
    await db.execute(delete(Cobranca))
    await db.execute(delete(Fatura))
    await db.execute(delete(Cliente))
    await db.commit()

    data = build_seed_data()

    for c in data["clientes"]:
        db.add(Cliente(**c))
    await db.commit()

    for f in data["faturas"]:
        db.add(Fatura(**f))
    await db.commit()

    for cob in data["cobrancas"]:
        db.add(Cobranca(**cob))
    await db.commit()

    return {
        "status": "ok",
        "seed": {
            "clientes": len(data["clientes"]),
            "faturas": len(data["faturas"]),
            "cobrancas": len(data["cobrancas"]),
        },
    }


@router.delete(
    "/reset",
    summary="Limpar todos os dados",
    description="Remove todos os registros de cobrancas, faturas e clientes. **Irreversível.**",
)
async def reset_database(
    db: AsyncSession = Depends(get_db),
    confirm: str = Query(..., description="Deve ser 'delete-all-data' para confirmar"),
):
    """Remove todos os registros do banco. Requer confirmação explícita.

    Args:
        db: Sessão assíncrona do banco (injetada).
        confirm: String de confirmação (deve ser 'delete-all-data').

    Returns:
        Dict com contagem de registros removidos por entidade.
    """
    _check_not_production()
    if confirm != "delete-all-data":
        raise APIError(
            status=400,
            error_type="confirmacao-necessaria",
            title="Confirmação necessária",
            detail="Envie ?confirm=delete-all-data para confirmar a operação.",
        )
    r_cob = await db.execute(delete(Cobranca))
    r_fat = await db.execute(delete(Fatura))
    r_cli = await db.execute(delete(Cliente))
    await db.commit()
    return {
        "status": "ok",
        "deleted": {
            "cobrancas": r_cob.rowcount,
            "faturas": r_fat.rowcount,
            "clientes": r_cli.rowcount,
        },
    }


@router.post(
    "/cleanup",
    summary="Limpeza de dados conforme LGPD",
    description="Executa política de retenção: anonimiza clientes inativos "
    "e remove mensagens de cobranças de faturas resolvidas além do período de retenção. "
    "Configurável via env vars RETENCAO_FATURAS_ANOS, RETENCAO_MENSAGENS_ANOS, "
    "RETENCAO_CLIENTES_INATIVOS_ANOS.",
)
async def cleanup(db: AsyncSession = Depends(get_db)):
    """Executa política de retenção LGPD (anonimização e limpeza de mensagens).

    Args:
        db: Sessão assíncrona do banco (injetada).

    Returns:
        Dict com resultado da limpeza (registros afetados).
    """
    return await cleanup_service.executar_cleanup(db)


@router.get(
    "/audit",
    summary="Consultar audit trail (LGPD Art. 37)",
    description="Lista registros de auditoria de acesso a dados pessoais.",
)
async def get_audit(
    recurso: str | None = Query(None, description="Filtrar por tipo de recurso"),
    recurso_id: str | None = Query(None, description="Filtrar por ID do recurso"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """Lista registros de auditoria de acesso a dados pessoais (LGPD Art. 37).

    Args:
        recurso: Tipo de recurso para filtrar (opcional).
        recurso_id: ID do recurso para filtrar (opcional).
        limit: Quantidade máxima de itens por página.
        offset: Deslocamento para paginação.
        db: Sessão assíncrona do banco (injetada).

    Returns:
        ListResponse com registros de auditoria paginados.
    """
    items, total = await audit_service.listar(
        db, recurso=recurso, recurso_id=recurso_id, limit=limit, offset=offset
    )
    return ListResponse(
        data=[
            {
                "id": a.id,
                "acao": a.acao,
                "recurso": a.recurso,
                "recurso_id": a.recurso_id,
                "detalhes": a.detalhes,
                "ip_address": a.ip_address,
                "created_at": a.created_at.isoformat() if a.created_at else None,
            }
            for a in items
        ],
        pagination=PaginationMeta(
            total=total,
            page_size=limit,
            has_more=(offset + limit) < total,
            offset=offset,
        ),
    )


@router.post(
    "/seed-regua",
    summary="Criar régua padrão UÚBA",
    description="Cria (ou recria) a régua de cobrança padrão com 5 passos progressivos.",
)
async def seed_regua(request: Request, db: AsyncSession = Depends(get_db)):
    """Cria ou recria a régua de cobrança padrão com 5 passos. Idempotente.

    Args:
        request: Request HTTP (usado para extrair tenant_id).
        db: Sessão assíncrona do banco (injetada).

    Returns:
        Dict com nome da régua e quantidade de passos criados.
    """
    from sqlalchemy import select, delete as sql_delete

    tenant_id = request.state.tenant_id
    data = build_regua_seed(tenant_id)

    # Idempotente: remove régua existente e recria
    existing = await db.execute(select(Regua).where(Regua.id == data["regua"]["id"]))
    if existing.scalar_one_or_none():
        await db.execute(sql_delete(ReguaPasso).where(ReguaPasso.regua_id == data["regua"]["id"]))
        await db.execute(sql_delete(Regua).where(Regua.id == data["regua"]["id"]))
        await db.commit()

    db.add(Regua(**data["regua"]))
    await db.commit()

    for passo in data["passos"]:
        db.add(ReguaPasso(**passo))
    await db.commit()

    return {
        "status": "ok",
        "regua": data["regua"]["nome"],
        "passos": len(data["passos"]),
    }
