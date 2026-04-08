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

_UUBA_SVG = """<svg width="48" height="48" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
<circle cx="52" cy="50" r="38" stroke="{color}" stroke-width="2.5" fill="none"/>
<path d="M14 50 C14 50 30 85 52 88 C52 88 14 82 14 50Z" fill="{color}"/>
<g stroke="{color}" stroke-width="1.8" stroke-linecap="round">
<line x1="28" y1="62" x2="72" y2="52"/><line x1="30" y1="67" x2="74" y2="57"/>
<line x1="33" y1="72" x2="76" y2="62"/><line x1="37" y1="77" x2="77" y2="67"/>
<line x1="42" y1="81" x2="76" y2="72"/><line x1="48" y1="84" x2="73" y2="76"/>
</g></svg>"""

_BASE_STYLE = """
<style>
  @import url('https://fonts.googleapis.com/css2?family=Libre+Baskerville&display=swap');
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: 'Libre Baskerville', Georgia, serif;
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #FAFAFA;
    color: #1A1A1A;
  }
  .card {
    text-align: center;
    padding: 60px 48px;
    max-width: 440px;
  }
  .logo { margin-bottom: 32px; }
  h1 {
    font-family: -apple-system, 'Helvetica Neue', sans-serif;
    font-weight: 300;
    font-size: 22px;
    letter-spacing: 0.02em;
    margin-bottom: 12px;
    color: {heading_color};
  }
  p {
    font-size: 15px;
    line-height: 1.6;
    color: #555;
  }
  .hint {
    margin-top: 24px;
    font-size: 13px;
    color: #999;
  }
</style>
"""

HTML_SUCCESS = (
    '<!DOCTYPE html><html lang="pt-BR"><head><meta charset="UTF-8">'
    '<meta name="viewport" content="width=device-width,initial-scale=1">'
    "<title>Autorizado - UUBA</title>"
    + _BASE_STYLE.replace("{heading_color}", "#1B2154")
    + '</head><body><div class="card">'
    + '<div class="logo">' + _UUBA_SVG.replace("{color}", "#1B2154") + "</div>"
    + "<h1>Autorizado com sucesso</h1>"
    + "<p>Sua integração foi conectada. Pode fechar esta janela.</p>"
    + '<p class="hint">UUBA Tech</p>'
    + "</div></body></html>"
)

HTML_ERROR = (
    '<!DOCTYPE html><html lang="pt-BR"><head><meta charset="UTF-8">'
    '<meta name="viewport" content="width=device-width,initial-scale=1">'
    "<title>Erro - UUBA</title>"
    + _BASE_STYLE.replace("{heading_color}", "#C0392B")
    + '</head><body><div class="card">'
    + '<div class="logo">' + _UUBA_SVG.replace("{color}", "#C0392B") + "</div>"
    + "<h1>Erro na autorização</h1>"
    + "<p>__MESSAGE__</p>"
    + '<p class="hint">UUBA Tech</p>'
    + "</div></body></html>"
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
