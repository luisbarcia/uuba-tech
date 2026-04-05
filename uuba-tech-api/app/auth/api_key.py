"""Autenticacao por API key com suporte a Unkey verify e fallback DB.

Em producao, valida via Unkey API (https://api.unkey.com/v2/keys.verifyKey).
Em dev/teste, faz fallback para lookup na DB local.

O Unkey v2 retorna ``identity.externalId`` (tenant_id) e ``permissions`` na response.
"""

import hmac as _hmac
import logging
import os
import time

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
UNKEY_ROOT_KEY = os.environ.get("UNKEY_ROOT_KEY", "")

CACHE_TTL_SECONDS = 300  # 5 minutos
CACHE_MAX_SIZE = 500  # Previne memory exhaustion por API keys distintas

# Cache com TTL: dict[key, (value, timestamp)]
_tenant_cache: dict[str, tuple[Tenant, float]] = {}
_unkey_cache: dict[str, tuple[dict, float]] = {}


def _get_cached(cache: dict, key: str):
    """Retorna valor cacheado se dentro do TTL, senao None."""
    entry = cache.get(key)
    if entry is None:
        return None
    value, ts = entry
    if time.monotonic() - ts > CACHE_TTL_SECONDS:
        del cache[key]
        return None
    return value


def _set_cached(cache: dict, key: str, value):
    """Armazena valor no cache com timestamp atual. Evicta entradas antigas se cheio."""
    if len(cache) >= CACHE_MAX_SIZE:
        # Evicta a entrada mais antiga (FIFO simples)
        oldest_key = min(cache, key=lambda k: cache[k][1])
        del cache[oldest_key]
    cache[key] = (value, time.monotonic())


def _is_unkey_enabled() -> bool:
    """Retorna True se Unkey verify esta habilitado.

    Habilitado quando UNKEY_ENABLED=1 ou UNKEY_ENABLED=true.
    Desabilitado por padrao e em testes (TESTING=1).
    """
    if os.environ.get("TESTING") == "1":
        return False
    return os.environ.get("UNKEY_ENABLED", "").lower() in ("1", "true")


async def _verify_via_unkey(api_key: str) -> dict:
    """Valida API key via Unkey API v2. Retorna dict com tenant_id, permissions, key_id.

    Mudancas v2:
    - Authorization header obrigatorio com root key (#77)
    - Response envelopada em meta/data (#78)
    - ownerId substituido por identity.externalId (#79)
    """
    if not UNKEY_ROOT_KEY:
        logger.error("UNKEY_ROOT_KEY vazio — Authorization header sera omitido")
        raise APIError(
            503,
            "auth-config",
            "Servico de autenticacao mal configurado",
            "UNKEY_ROOT_KEY nao definido. Configure no ambiente do container.",
        )

    cached = _get_cached(_unkey_cache, api_key)
    if cached:
        return cached

    try:
        headers = {"Authorization": f"Bearer {UNKEY_ROOT_KEY}"}
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(
                UNKEY_VERIFY_URL,
                headers=headers,
                json={"key": api_key},
            )
        body = response.json()
    except (httpx.HTTPError, Exception) as exc:
        logger.error(f"Unkey verify falhou: {exc}")
        raise APIError(
            503,
            "auth-indisponivel",
            "Servico de autenticacao indisponivel",
            "Nao foi possivel validar a API key. Tente novamente.",
        )

    # v2 envelopa em {meta, data} — fallback para flat (v1 compat)
    data = body.get("data", body)

    if not data.get("valid"):
        raise APIError(
            401,
            "auth-invalida",
            "Autenticacao invalida",
            "API key ausente ou invalida",
        )

    # v2: identity.externalId substitui ownerId
    identity = data.get("identity") or {}
    tenant_id = identity.get("externalId", "") or data.get("ownerId", "")

    result = {
        "tenant_id": tenant_id,
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

    _set_cached(_unkey_cache, api_key, result)
    return result


async def _verify_via_db(api_key: str, db: AsyncSession) -> str:
    """Fallback: valida API key via DB local. Retorna tenant_id."""
    tenant = _get_cached(_tenant_cache, api_key)

    if not tenant:
        result = await db.execute(select(Tenant).where(Tenant.ativo.is_(True)))
        tenants = result.scalars().all()
        for t in tenants:
            if t.api_key and _hmac.compare_digest(api_key, t.api_key):
                tenant = t
                _set_cached(_tenant_cache, api_key, t)
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
        request.state.permissions = ["*"]  # DB fallback: full access (Unkey disabled)
        request.state.key_id = ""

    return api_key


def require_permission(permission: str):
    """FastAPI dependency — verifica se o request tem uma permissao especifica.

    Deve ser usado APOS verify_api_key (que seta request.state.permissions).

    Args:
        permission: String de permissao (ex: "tenants:write").

    Raises:
        APIError 403 se a permissao nao estiver presente.
    """

    async def _check(request: Request):
        permissions = getattr(request.state, "permissions", [])
        if permission not in permissions:
            raise APIError(
                403,
                "permissao-negada",
                "Permissao negada",
                f"Esta operacao requer a permissao '{permission}'.",
            )

    return _check


def clear_tenant_cache() -> None:
    """Limpa cache de tenants (util em testes)."""
    _tenant_cache.clear()
    _unkey_cache.clear()
