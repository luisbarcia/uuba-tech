"""Router de integracoes — endpoint para consumers (n8n, scripts) buscarem credenciais.

Descriptografa credenciais AES-256-GCM, faz auto-refresh de OAuth tokens expirados,
e usa pg_advisory_lock para evitar refreshes concorrentes.

Ref: docs/specs/integrations-module.spec.md (FR-API-001, FR-API-002, FR-API-003)
"""

import hashlib
import json
import logging
import os
from datetime import datetime, timezone

import httpx
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from fastapi import APIRouter, Depends, Request
from sqlalchemy import select, text, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.api_key import require_permission, verify_api_key
from app.database import get_db
from app.exceptions import APIError
from app.models.integration import (
    IntegrationCredential,
    IntegrationEvent,
    IntegrationProvider,
    TenantIntegration,
)
from app.utils.ids import generate_id

logger = logging.getLogger("uuba")

router = APIRouter(
    prefix="/api/v1/integrations",
    tags=["integrations"],
    dependencies=[Depends(verify_api_key)],
)


def _get_encryption_key() -> str:
    """Obtem chave de encriptacao do env var. Levanta APIError se ausente."""
    key = os.environ.get("INTEGRATION_ENCRYPTION_KEY", "")
    if not key:
        raise APIError(
            503,
            "integracao-config",
            "Chave de encriptacao nao configurada",
            "Defina INTEGRATION_ENCRYPTION_KEY no ambiente.",
        )
    return key


def _derive_key(raw_key: str) -> bytes:
    """Deriva chave AES-256 de 32 bytes via SHA-256. Compativel com o CLI (Node.js)."""
    return hashlib.sha256(raw_key.encode()).digest()


def decrypt_credentials(encrypted_data: bytes, iv: bytes, key: str) -> dict:
    """Descriptografa credenciais encriptadas com AES-256-GCM.

    O CLI (Node.js) usa ``crypto.createCipheriv("aes-256-gcm")``,
    que concatena ciphertext + auth_tag (16 bytes) em ``encrypted_data``.
    A lib ``cryptography`` do Python espera exatamente esse formato
    no metodo ``AESGCM.decrypt(nonce, data, aad)``.

    Args:
        encrypted_data: Ciphertext + auth_tag (16 bytes) do DB (BYTEA).
        iv: Initialization vector (12 bytes) do DB (BYTEA).
        key: Chave raw do env var INTEGRATION_ENCRYPTION_KEY.

    Returns:
        dict com credenciais descriptografadas.
    """
    derived = _derive_key(key)
    aesgcm = AESGCM(derived)
    plaintext = aesgcm.decrypt(iv, encrypted_data, None)
    return json.loads(plaintext.decode())


async def _refresh_oauth_token(
    db: AsyncSession,
    integration: TenantIntegration,
    credential: IntegrationCredential,
    provider: IntegrationProvider,
    encryption_key: str,
) -> dict:
    """Faz refresh do OAuth token usando token_url do provider.

    Usa pg_advisory_lock para evitar refreshes concorrentes.
    Registra evento "refreshed" ou "error" no historico.

    Returns:
        dict com credenciais atualizadas (plaintext).
    """
    if not provider.token_url:
        raise APIError(
            502,
            "integracao-refresh-falhou",
            "Refresh nao suportado",
            f"Provider {provider.slug} nao tem token_url configurado.",
        )

    # Advisory lock baseado no hash do integration_id para evitar refreshes concorrentes
    lock_key = int(hashlib.md5(integration.id.encode()).hexdigest()[:15], 16) & 0x7FFFFFFF
    lock_result = await db.execute(text(f"SELECT pg_try_advisory_lock({lock_key})"))
    got_lock = lock_result.scalar()

    if not got_lock:
        # Outro request esta fazendo refresh — aguarda e tenta ler credenciais atualizadas
        await db.execute(text(f"SELECT pg_advisory_lock({lock_key})"))
        await db.execute(text(f"SELECT pg_advisory_unlock({lock_key})"))
        # Re-ler credencial atualizada pelo outro request
        await db.refresh(credential)
        return decrypt_credentials(credential.encrypted_data, credential.iv, encryption_key)

    try:
        current_creds = decrypt_credentials(
            credential.encrypted_data, credential.iv, encryption_key
        )
        refresh_token = current_creds.get("refresh_token")
        if not refresh_token:
            raise APIError(
                502,
                "integracao-refresh-falhou",
                "Refresh token ausente",
                "Credenciais nao contem refresh_token. Reconecte via CLI.",
            )

        # Fazer request de refresh
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                provider.token_url,
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

        if response.status_code != 200:
            # Registrar evento de erro
            integration.error_count += 1
            integration.error_message = f"Refresh falhou: HTTP {response.status_code}"
            integration.last_error_at = datetime.now(timezone.utc)
            if integration.error_count >= 5:
                integration.status = "suspended"

            db.add(
                IntegrationEvent(
                    id=generate_id("iev"),
                    integration_id=integration.id,
                    event_type="error",
                    details={
                        "action": "refresh",
                        "http_status": response.status_code,
                        "body": response.text[:500],
                    },
                    created_at=datetime.now(timezone.utc),
                )
            )
            await db.commit()

            raise APIError(
                502,
                "integracao-refresh-falhou",
                "Refresh de token falhou",
                f"Provider retornou HTTP {response.status_code}. "
                "Reconecte via `uuba integrations credentials set`.",
            )

        token_data = response.json()

        # Atualizar credenciais com novos tokens
        new_creds = {**current_creds, **token_data}
        if "refresh_token" not in token_data:
            new_creds["refresh_token"] = refresh_token

        # Encriptar e salvar
        derived = _derive_key(encryption_key)
        aesgcm = AESGCM(derived)
        new_iv = os.urandom(12)
        new_encrypted = aesgcm.encrypt(new_iv, json.dumps(new_creds).encode(), None)

        credential.encrypted_data = new_encrypted
        credential.iv = new_iv
        credential.last_refreshed_at = datetime.now(timezone.utc)
        if token_data.get("expires_in"):
            from datetime import timedelta

            credential.token_expires_at = datetime.now(timezone.utc) + timedelta(
                seconds=token_data["expires_in"]
            )

        # Resetar error_count e status
        integration.error_count = 0
        integration.error_message = None
        integration.status = "active"

        # Registrar evento
        db.add(
            IntegrationEvent(
                id=generate_id("iev"),
                integration_id=integration.id,
                event_type="refreshed",
                details={"expires_in": token_data.get("expires_in")},
                created_at=datetime.now(timezone.utc),
            )
        )
        await db.commit()

        return new_creds

    finally:
        await db.execute(text(f"SELECT pg_advisory_unlock({lock_key})"))


@router.get(
    "/{tenant_id}/{provider_slug}/credentials",
    summary="Buscar credenciais de integracao",
    description="Descriptografa e retorna credenciais de uma integracao. "
    "Se o token OAuth estiver expirado, faz auto-refresh transparente. "
    "Protegido por scope `integrations:read`.",
    dependencies=[Depends(require_permission("integrations:read"))],
)
async def get_integration_credentials(
    request: Request,
    tenant_id: str,
    provider_slug: str,
    db: AsyncSession = Depends(get_db),
):
    """GET /api/v1/integrations/{tenant_id}/{provider_slug}/credentials

    Retorna credenciais descriptografadas, connection_config e status.
    Se token_expires_at < now(), faz auto-refresh usando token_url do provider.
    """
    # Verificar que o tenant_id do path corresponde ao da API key
    auth_tenant_id = request.state.tenant_id
    if auth_tenant_id != tenant_id:
        raise APIError(
            403,
            "permissao-negada",
            "Permissao negada",
            f"API key pertence ao tenant {auth_tenant_id}, nao {tenant_id}.",
        )

    # Buscar provider
    result = await db.execute(
        select(IntegrationProvider).where(
            and_(
                IntegrationProvider.slug == provider_slug,
                IntegrationProvider.is_active.is_(True),
            )
        )
    )
    provider = result.scalar_one_or_none()
    if not provider:
        raise APIError(
            404,
            "provider-nao-encontrado",
            "Provider nao encontrado",
            f"Provider '{provider_slug}' nao existe ou esta inativo.",
        )

    # Buscar integracao do tenant
    result = await db.execute(
        select(TenantIntegration).where(
            and_(
                TenantIntegration.tenant_id == tenant_id,
                TenantIntegration.provider_id == provider.id,
                TenantIntegration.enabled.is_(True),
            )
        )
    )
    integration = result.scalar_one_or_none()
    if not integration:
        raise APIError(
            404,
            "integracao-nao-encontrada",
            "Integracao nao encontrada",
            f"Nenhuma integracao ativa para provider '{provider_slug}' no tenant {tenant_id}.",
        )

    if integration.status == "suspended":
        raise APIError(
            503,
            "integracao-suspensa",
            "Integracao suspensa",
            "Integracao suspensa por erros consecutivos. Reative via `uuba integrations enable`.",
        )

    if integration.status in ("pending_setup", "configuring"):
        raise APIError(
            409,
            "integracao-sem-credenciais",
            "Credenciais nao configuradas",
            f"Integracao em status '{integration.status}'. "
            "Configure credenciais via `uuba integrations credentials set`.",
        )

    # Buscar credenciais
    result = await db.execute(
        select(IntegrationCredential).where(IntegrationCredential.integration_id == integration.id)
    )
    credential = result.scalar_one_or_none()
    if not credential:
        raise APIError(
            404,
            "credenciais-nao-encontradas",
            "Credenciais nao encontradas",
            "Integracao existe mas nao tem credenciais. "
            "Configure via `uuba integrations credentials set`.",
        )

    encryption_key = _get_encryption_key()

    # Verificar se token expirou (auto-refresh)
    now = datetime.now(timezone.utc)
    needs_refresh = (
        provider.auth_type in ("OAUTH2", "OAUTH2_CC")
        and credential.token_expires_at is not None
        and credential.token_expires_at < now
    )

    if needs_refresh:
        creds = await _refresh_oauth_token(db, integration, credential, provider, encryption_key)
    else:
        creds = decrypt_credentials(credential.encrypted_data, credential.iv, encryption_key)

    # Atualizar last_used_at
    credential.last_used_at = now
    await db.commit()

    return {
        "access_token": creds.get("access_token", creds.get("api_key", "")),
        "token_type": creds.get("token_type", "bearer"),
        "scope": creds.get("scope", ""),
        "connection_config": integration.connection_config,
        "status": integration.status,
        "provider": {
            "slug": provider.slug,
            "name": provider.name,
            "auth_type": provider.auth_type,
            "base_url": provider.base_url,
        },
    }
