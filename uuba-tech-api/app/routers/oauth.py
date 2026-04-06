"""Router OAuth — state tokens + callback para fluxo Authorization Code + PKCE.

Endpoints:
- POST /api/v1/integrations/oauth/state  (protected)
- GET  /api/v1/integrations/oauth/state/{state_token}  (protected)
- GET  /oauth/callback  (public — chamado pelo browser do tenant)
"""

import logging
import os
from datetime import datetime, timezone, timedelta

import httpx
from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import select, and_
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
from app.models.oauth_state import OAuthStateToken
from app.routers.integrations import encrypt_credentials, _get_encryption_key
from app.utils.ids import generate_id

logger = logging.getLogger("uuba")


def _ensure_aware(dt: datetime) -> datetime:
    """Garante que datetime eh timezone-aware (UTC). SQLite retorna naive."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt

# --- Router protegido (state CRUD) ---
state_router = APIRouter(
    prefix="/api/v1/integrations/oauth",
    tags=["integrations"],
    dependencies=[Depends(verify_api_key)],
)


@state_router.post(
    "/state",
    status_code=201,
    summary="Criar state token para fluxo OAuth",
    description="Cria um state token com PKCE para iniciar o fluxo OAuth2 Authorization Code. "
    "Token expira em 60 minutos. Protegido por scope `integrations:write`.",
    dependencies=[Depends(require_permission("integrations:write"))],
)
async def create_state_token(
    body: dict,
    db: AsyncSession = Depends(get_db),
):
    """POST /api/v1/integrations/oauth/state

    Body: integration_id, provider_slug, scopes, code_verifier, redirect_uri
    """
    integration_id = body.get("integration_id", "")
    provider_slug = body.get("provider_slug", "")
    redirect_uri = body.get("redirect_uri", "")

    if not integration_id or not provider_slug or not redirect_uri:
        raise APIError(
            422,
            "validacao",
            "Campos obrigatorios ausentes",
            "integration_id, provider_slug e redirect_uri sao obrigatorios.",
        )

    state = OAuthStateToken.generate_state()
    now = datetime.now(timezone.utc)

    token = OAuthStateToken(
        id=generate_id("ost"),
        state_token=state,
        integration_id=integration_id,
        provider_slug=provider_slug,
        scopes=body.get("scopes"),
        code_verifier=body.get("code_verifier"),
        redirect_uri=redirect_uri,
        status="pending",
        expires_at=now + timedelta(minutes=60),
        created_at=now,
    )
    db.add(token)
    await db.commit()

    return {
        "state_token": state,
        "expires_at": token.expires_at.isoformat(),
    }


@state_router.get(
    "/state/{state_token}",
    summary="Consultar status de state token OAuth",
    description="Retorna o status atual (pending, completed, expired) de um state token. "
    "Se expirado, marca automaticamente como expired. Protegido por scope `integrations:read`.",
    dependencies=[Depends(require_permission("integrations:read"))],
)
async def poll_state_token(
    state_token: str,
    db: AsyncSession = Depends(get_db),
):
    """GET /api/v1/integrations/oauth/state/{state_token}"""
    result = await db.execute(
        select(OAuthStateToken).where(OAuthStateToken.state_token == state_token)
    )
    token = result.scalar_one_or_none()

    if not token:
        raise APIError(
            404,
            "state-nao-encontrado",
            "State token nao encontrado",
            f"State token '{state_token}' nao existe.",
        )

    # Auto-expire
    now = datetime.now(timezone.utc)
    if token.status == "pending" and _ensure_aware(token.expires_at) < now:
        token.status = "expired"
        await db.commit()

    return {
        "status": token.status,
        "integration_id": token.integration_id,
    }


# --- Router publico (callback) ---
callback_router = APIRouter(tags=["integrations"])

HTML_SUCCESS = """<!DOCTYPE html>
<html lang="pt-BR">
<head><meta charset="UTF-8"><title>Autorizado</title></head>
<body style="font-family:sans-serif;text-align:center;padding:60px">
<h1>Autorizado com sucesso!</h1>
<p>Pode fechar esta janela.</p>
</body>
</html>"""

HTML_ERROR = """<!DOCTYPE html>
<html lang="pt-BR">
<head><meta charset="UTF-8"><title>Erro</title></head>
<body style="font-family:sans-serif;text-align:center;padding:60px">
<h1>Erro na autorização</h1>
<p>{message}</p>
</body>
</html>"""


@callback_router.get(
    "/oauth/callback",
    response_class=HTMLResponse,
    summary="Callback OAuth (chamado pelo browser)",
    description="Endpoint publico chamado pelo provider OAuth apos autorizacao. "
    "Troca o authorization code por tokens, encripta e salva no cofre.",
)
async def oauth_callback(
    code: str = Query(...),
    state: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """GET /oauth/callback?code=xxx&state=yyy

    Fluxo:
    1. Buscar state token
    2. Validar: exists, pending, not expired
    3. Buscar provider config
    4. POST token_url com authorization code + PKCE
    5. Encriptar tokens e salvar no cofre
    6. Atualizar integration status para active
    7. Criar evento connected
    8. Marcar state como completed
    """
    # 1. Buscar state token
    result = await db.execute(
        select(OAuthStateToken).where(OAuthStateToken.state_token == state)
    )
    token = result.scalar_one_or_none()

    if not token:
        return HTMLResponse(
            content=HTML_ERROR.format(message="State token inválido ou não encontrado."),
            status_code=400,
        )

    # 2. Validar
    now = datetime.now(timezone.utc)
    if token.status != "pending":
        return HTMLResponse(
            content=HTML_ERROR.format(message=f"State token já foi utilizado (status: {token.status})."),
            status_code=400,
        )

    if _ensure_aware(token.expires_at) < now:
        token.status = "expired"
        await db.commit()
        return HTMLResponse(
            content=HTML_ERROR.format(message="State token expirado. Inicie o fluxo novamente."),
            status_code=400,
        )

    # 3. Buscar provider config
    result = await db.execute(
        select(IntegrationProvider).where(
            and_(
                IntegrationProvider.slug == token.provider_slug,
                IntegrationProvider.is_active.is_(True),
            )
        )
    )
    provider = result.scalar_one_or_none()

    if not provider or not provider.token_url:
        return HTMLResponse(
            content=HTML_ERROR.format(message="Provider não encontrado ou sem token_url configurado."),
            status_code=400,
        )

    # 4. Buscar client_id/secret dos env vars
    env_prefix = provider.slug.upper().replace("-", "_")
    client_id = os.environ.get(f"{env_prefix}_CLIENT_ID", "")
    client_secret = os.environ.get(f"{env_prefix}_CLIENT_SECRET", "")

    if not client_id or not client_secret:
        logger.error(f"OAuth callback: {env_prefix}_CLIENT_ID ou _CLIENT_SECRET ausente")
        return HTMLResponse(
            content=HTML_ERROR.format(message="Configuração do provider incompleta no servidor."),
            status_code=400,
        )

    # 5. POST token_url
    token_data_payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": token.redirect_uri,
    }
    if token.code_verifier:
        token_data_payload["code_verifier"] = token.code_verifier

    try:
        async with httpx.AsyncClient(timeout=15.0) as http_client:
            response = await http_client.post(
                provider.token_url,
                data=token_data_payload,
                auth=(client_id, client_secret),
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
    except httpx.HTTPError as exc:
        logger.error(f"OAuth token exchange falhou: {exc}")
        return HTMLResponse(
            content=HTML_ERROR.format(message="Falha na comunicação com o provider."),
            status_code=400,
        )

    if response.status_code != 200:
        logger.error(f"OAuth token exchange HTTP {response.status_code}: {response.text[:500]}")
        return HTMLResponse(
            content=HTML_ERROR.format(message="Provider rejeitou a troca de código por tokens."),
            status_code=400,
        )

    token_data = response.json()

    # 6. Encriptar tokens e salvar no cofre
    encryption_key = _get_encryption_key()
    encrypted_data, iv = encrypt_credentials(token_data, encryption_key)

    # Buscar integracao
    result = await db.execute(
        select(TenantIntegration).where(TenantIntegration.id == token.integration_id)
    )
    integration = result.scalar_one_or_none()

    if not integration:
        return HTMLResponse(
            content=HTML_ERROR.format(message="Integração não encontrada."),
            status_code=400,
        )

    # Upsert credential
    result = await db.execute(
        select(IntegrationCredential).where(
            IntegrationCredential.integration_id == integration.id
        )
    )
    credential = result.scalar_one_or_none()

    if credential:
        credential.encrypted_data = encrypted_data
        credential.iv = iv
        credential.updated_at = now
        if token_data.get("expires_in"):
            credential.token_expires_at = now + timedelta(seconds=token_data["expires_in"])
    else:
        credential = IntegrationCredential(
            id=generate_id("crd"),
            integration_id=integration.id,
            encrypted_data=encrypted_data,
            iv=iv,
            created_at=now,
            updated_at=now,
        )
        if token_data.get("expires_in"):
            credential.token_expires_at = now + timedelta(seconds=token_data["expires_in"])
        db.add(credential)

    # 7. Atualizar integration status para active
    integration.status = "active"
    integration.error_count = 0
    integration.error_message = None

    # 8. Criar evento connected
    db.add(
        IntegrationEvent(
            id=generate_id("iev"),
            integration_id=integration.id,
            event_type="connected",
            details={"method": "oauth_callback", "scopes": token.scopes or ""},
            created_at=now,
        )
    )

    # 9. Marcar state como completed
    token.status = "completed"

    await db.commit()

    # 10. Retornar HTML de sucesso
    return HTMLResponse(content=HTML_SUCCESS, status_code=200)


# --- Router combinado para registrar em main.py ---
router = APIRouter()
router.include_router(state_router)
router.include_router(callback_router)
