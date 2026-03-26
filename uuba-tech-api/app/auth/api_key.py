"""Autenticacao por API key com suporte a Unkey verify e fallback DB.

Em producao, valida via Unkey API (https://api.unkey.com/v2/keys.verifyKey).
Em dev/teste, faz fallback para lookup na DB local.

O Unkey retorna ``ownerId`` (tenant_id) e ``permissions`` na response.
"""

import hmac as _hmac
import logging
import os

import httpx
from fastapi import Depends, Request, Security
from fastapi.security import APIKeyHeader
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.exceptions import APIError
from app.models.tenant import Tenant

logger = logging.getLogger("uuba")

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

UNKEY_VERIFY_URL = "https://api.unkey.com/v2/keys.verifyKey"

# Cache simples em memoria (tenant por api_key) — usado no fallback DB
_tenant_cache: dict[str, Tenant] = {}

# Cache para respostas do Unkey (evita chamadas repetidas)
_unkey_cache: dict[str, dict] = {}


def _is_unkey_enabled() -> bool:
    """Retorna True se Unkey verify esta habilitado.

    Habilitado quando UNKEY_ENABLED=1 ou UNKEY_ENABLED=true.
    Desabilitado por padrao e em testes (TESTING=1).
    """
    if os.environ.get("TESTING") == "1":
        return False
    return os.environ.get("UNKEY_ENABLED", "").lower() in ("1", "true")


async def _verify_via_unkey(api_key: str) -> dict:
    """Valida API key via Unkey API. Retorna dict com tenant_id, permissions, key_id."""
    cached = _unkey_cache.get(api_key)
    if cached:
        return cached

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(
                UNKEY_VERIFY_URL,
                json={"key": api_key},
            )
        data = response.json()
    except (httpx.HTTPError, Exception) as exc:
        logger.error(f"Unkey verify falhou: {exc}")
        raise APIError(
            503,
            "auth-indisponivel",
            "Servico de autenticacao indisponivel",
            "Nao foi possivel validar a API key. Tente novamente.",
        )

    if not data.get("valid"):
        raise APIError(
            401,
            "auth-invalida",
            "Autenticacao invalida",
            "API key ausente ou invalida",
        )

    result = {
        "tenant_id": data.get("ownerId", ""),
        "permissions": data.get("permissions", []),
        "key_id": data.get("keyId", ""),
    }

    if not result["tenant_id"]:
        raise APIError(
            401,
            "auth-invalida",
            "Autenticacao invalida",
            "API key nao esta associada a um tenant.",
        )

    _unkey_cache[api_key] = result
    return result


async def _verify_via_db(api_key: str, db: AsyncSession) -> str:
    """Fallback: valida API key via DB local. Retorna tenant_id."""
    tenant = _tenant_cache.get(api_key)

    if not tenant:
        result = await db.execute(select(Tenant).where(Tenant.ativo.is_(True)))
        tenants = result.scalars().all()
        for t in tenants:
            if t.api_key and _hmac.compare_digest(api_key, t.api_key):
                tenant = t
                _tenant_cache[api_key] = t
                break

    if not tenant:
        raise APIError(
            401,
            "auth-invalida",
            "Autenticacao invalida",
            "API key ausente ou invalida",
        )

    return tenant.id


async def verify_api_key(
    request: Request,
    api_key: str | None = Security(api_key_header),
    db: AsyncSession = Depends(get_db),
) -> str:
    """Valida API key e identifica o tenant.

    Injeta ``request.state.tenant_id`` para uso nos endpoints.

    Em producao com UNKEY_ENABLED=1, valida via Unkey API.
    Caso contrario, faz fallback para lookup na DB local.
    """
    if not api_key:
        raise APIError(
            401,
            "auth-invalida",
            "Autenticacao invalida",
            "API key ausente ou invalida",
        )

    if _is_unkey_enabled():
        unkey_data = await _verify_via_unkey(api_key)
        request.state.tenant_id = unkey_data["tenant_id"]
        request.state.permissions = unkey_data["permissions"]
        request.state.key_id = unkey_data["key_id"]
    else:
        tenant_id = await _verify_via_db(api_key, db)
        request.state.tenant_id = tenant_id
        request.state.permissions = []
        request.state.key_id = ""

    return api_key


def clear_tenant_cache() -> None:
    """Limpa cache de tenants (util em testes)."""
    _tenant_cache.clear()
    _unkey_cache.clear()
