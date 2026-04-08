"""Router OAuth — state tokens + callback para fluxo Authorization Code + PKCE.

Endpoints:
- POST /api/v1/integrations/oauth/state  (protected)
- GET  /api/v1/integrations/oauth/state/{state_token}  (protected)
- GET  /oauth/callback  (public — chamado pelo browser do tenant)
"""

import logging
from datetime import datetime, timezone, timedelta

import httpx
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
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
from app.models.oauth_app import OAuthApp
from app.models.oauth_state import OAuthStateToken
from app.routers.integrations import encrypt_credentials, _get_encryption_key, _derive_key
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

_STYLE = (
    '<style>'
    '@import url("https://fonts.googleapis.com/css2?family=Source+Serif+4:wght@400;600&display=swap");'
    '*{margin:0;padding:0;box-sizing:border-box}'
    'body{font-family:"Source Serif 4",Georgia,serif;min-height:100vh;display:flex;align-items:center;justify-content:center;background:#FAFAFA;color:#1A1A1A}'
    '.card{text-align:center;padding:60px 48px;max-width:440px}'
    '.logo{margin-bottom:32px}'
    '.logo img{width:64px;height:64px}'
    'h1{font-weight:600;font-size:20px;letter-spacing:0.01em;margin-bottom:12px}'
    'p{font-size:15px;line-height:1.7;color:#555}'
    '.brand{margin-top:32px;font-size:12px;letter-spacing:0.15em;text-transform:uppercase;color:#BBB}'
    '</style>'
)

_LOGO_NAVY = "data:image/png;base64,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"
_LOGO_RED = "data:image/png;base64,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"

HTML_SUCCESS = (
    '<!DOCTYPE html><html lang="pt-BR"><head><meta charset="UTF-8">'
    '<meta name="viewport" content="width=device-width,initial-scale=1">'
    '<title>Autorizado - UUBA</title>'
    + _STYLE
    + '</head><body><div class="card">'
    '<div class="logo"><img src="' + _LOGO_NAVY + '" alt="UUBA"></div>'
    '<h1 style="color:#1B2154">Autorizado com sucesso</h1>'
    '<p>Sua integracao foi conectada. Pode fechar esta janela.</p>'
    '<p class="brand">uuba tech</p>'
    '</div></body></html>'
)

HTML_ERROR = (
    '<!DOCTYPE html><html lang="pt-BR"><head><meta charset="UTF-8">'
    '<meta name="viewport" content="width=device-width,initial-scale=1">'
    '<title>Erro - UUBA</title>'
    + _STYLE
    + '</head><body><div class="card">'
    '<div class="logo"><img src="' + _LOGO_RED + '" alt="UUBA"></div>'
    '<h1 style="color:#C0392B">Erro na autorizacao</h1>'
    '<p>__MESSAGE__</p>'
    '<p class="brand">uuba tech</p>'
    '</div></body></html>'
)


def _error_page(message: str) -> str:
    """Gera pagina de erro com mensagem substituida."""
    return HTML_ERROR.replace("__MESSAGE__", message)



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
            content=_error_page("State token inválido ou não encontrado."),
            status_code=400,
        )

    # 2. Validar
    now = datetime.now(timezone.utc)
    if token.status != "pending":
        return HTMLResponse(
            content=_error_page(f"State token já foi utilizado (status: {token.status})."),
            status_code=400,
        )

    if _ensure_aware(token.expires_at) < now:
        token.status = "expired"
        await db.commit()
        return HTMLResponse(
            content=_error_page("State token expirado. Inicie o fluxo novamente."),
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
            content=_error_page("Provider não encontrado ou sem token_url configurado."),
            status_code=400,
        )

    # 4. Buscar integracao (movido para antes do OAuth app lookup)
    result = await db.execute(
        select(TenantIntegration).where(TenantIntegration.id == token.integration_id)
    )
    integration = result.scalar_one_or_none()

    if not integration:
        return HTMLResponse(
            content=_error_page("Integração não encontrada."),
            status_code=400,
        )

    # 5. Resolver OAuth app do DB (oauth_apps table)
    # Prioridade: integration.oauth_app_id → default do provider → erro
    oauth_app = None
    if integration.oauth_app_id:
        result = await db.execute(
            select(OAuthApp).where(OAuthApp.id == integration.oauth_app_id)
        )
        oauth_app = result.scalar_one_or_none()

    if not oauth_app:
        # Fallback: default for this provider
        result = await db.execute(
            select(OAuthApp).where(
                and_(OAuthApp.provider_id == provider.id, OAuthApp.is_default.is_(True))
            )
        )
        oauth_app = result.scalar_one_or_none()

    if not oauth_app:
        logger.error(f"OAuth callback: nenhum OAuth app para provider {provider.slug}")
        return HTMLResponse(
            content=_error_page(
                "OAuth app não configurado para este provider. "
                "Configure via: uuba integrations oauth-apps add"
            ),
            status_code=400,
        )

    client_id = oauth_app.client_id
    # Decrypt client_secret
    encryption_key = _get_encryption_key()
    derived = _derive_key(encryption_key)
    aesgcm = AESGCM(derived)
    client_secret = aesgcm.decrypt(
        bytes(oauth_app.client_secret_iv),
        bytes(oauth_app.client_secret_encrypted),
        None,
    ).decode()

    # 6. POST token_url
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
            content=_error_page("Falha na comunicação com o provider."),
            status_code=400,
        )

    if response.status_code != 200:
        logger.error(f"OAuth token exchange HTTP {response.status_code}: {response.text[:500]}")
        return HTMLResponse(
            content=_error_page("Provider rejeitou a troca de código por tokens."),
            status_code=400,
        )

    token_data = response.json()

    # 7. Encriptar tokens e salvar no cofre
    encrypted_data, iv = encrypt_credentials(token_data, encryption_key)

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
