"""Autenticação por API key com tenant lookup.

Cada tenant tem sua própria API key. O middleware valida a key,
identifica o tenant e injeta tenant_id no request.state.
"""

import hmac as _hmac

from fastapi import Depends, Request, Security
from fastapi.security import APIKeyHeader
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.exceptions import APIError
from app.models.tenant import Tenant

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# Cache simples em memória (tenant por api_key)
_tenant_cache: dict[str, Tenant] = {}


async def verify_api_key(
    request: Request,
    api_key: str | None = Security(api_key_header),
    db: AsyncSession = Depends(get_db),
) -> str:
    """Valida API key e identifica o tenant.

    Injeta ``request.state.tenant_id`` para uso nos endpoints.
    Usa comparação constant-time para prevenir timing attacks.
    """
    if not api_key:
        raise APIError(
            401,
            "auth-invalida",
            "Autenticação inválida",
            "API key ausente ou inválida",
        )

    # Lookup no cache primeiro
    tenant = _tenant_cache.get(api_key)

    if not tenant:
        result = await db.execute(select(Tenant).where(Tenant.ativo.is_(True)))
        tenants = result.scalars().all()
        for t in tenants:
            if _hmac.compare_digest(api_key, t.api_key):
                tenant = t
                _tenant_cache[api_key] = t
                break

    if not tenant:
        raise APIError(
            401,
            "auth-invalida",
            "Autenticação inválida",
            "API key ausente ou inválida",
        )

    request.state.tenant_id = tenant.id
    return api_key


def clear_tenant_cache() -> None:
    """Limpa cache de tenants (útil em testes)."""
    _tenant_cache.clear()
