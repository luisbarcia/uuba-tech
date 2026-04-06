"""Testes para OAuth state tokens + callback.

Valida: create state, poll pending, poll expired, callback invalid, callback expired, no auth.
"""

import os
import pytest
from datetime import datetime, timezone, timedelta

from tests.conftest import AUTH, TEST_TENANT_ID
from app.models.integration import (
    IntegrationProvider,
    TenantIntegration,
)
from app.models.oauth_state import OAuthStateToken
from app.utils.ids import generate_id
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession


ENCRYPTION_KEY = "test_key_32_bytes_for_aes256_ok!"
PROVIDER_ID = "plat_conta_azul"
INTEGRATION_ID = "int_oauth_test"


@pytest.fixture(autouse=True)
def set_encryption_key():
    os.environ["INTEGRATION_ENCRYPTION_KEY"] = ENCRYPTION_KEY
    yield
    os.environ.pop("INTEGRATION_ENCRYPTION_KEY", None)


@pytest.fixture
async def seed_oauth_provider(engine):
    """Cria provider OAuth + integracao para testes."""
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        session.add(
            IntegrationProvider(
                id=PROVIDER_ID,
                slug="conta-azul",
                name="Conta Azul",
                category="erp",
                auth_type="OAUTH2",
                base_url="https://api.contaazul.com/v1",
                token_url="https://api.contaazul.com/oauth2/token",
                authorization_url="https://api.contaazul.com/oauth2/authorize",
                is_active=True,
                created_at=datetime.now(timezone.utc),
            )
        )
        session.add(
            TenantIntegration(
                id=INTEGRATION_ID,
                tenant_id=TEST_TENANT_ID,
                provider_id=PROVIDER_ID,
                display_name="Conta Azul Prod",
                status="pending_setup",
                enabled=True,
            )
        )
        await session.commit()
    return factory


@pytest.mark.asyncio
async def test_create_state_token(client, seed_oauth_provider):
    """POST cria state com 64 chars, status pending."""
    resp = await client.post(
        "/api/v1/integrations/oauth/state",
        json={
            "integration_id": INTEGRATION_ID,
            "provider_slug": "conta-azul",
            "scopes": "accounting",
            "code_verifier": "abc123verifier",
            "redirect_uri": "https://api.uuba.tech/oauth/callback",
        },
        headers=AUTH,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert "state_token" in data
    assert len(data["state_token"]) == 64
    assert "expires_at" in data

    # Verificar no DB
    async with seed_oauth_provider() as session:
        result = await session.execute(
            select(OAuthStateToken).where(
                OAuthStateToken.state_token == data["state_token"]
            )
        )
        token = result.scalar_one()
        assert token.status == "pending"
        assert token.integration_id == INTEGRATION_ID
        assert token.provider_slug == "conta-azul"
        assert token.code_verifier == "abc123verifier"


@pytest.mark.asyncio
async def test_poll_state_pending(client, seed_oauth_provider):
    """GET retorna status pending."""
    # Criar state
    resp = await client.post(
        "/api/v1/integrations/oauth/state",
        json={
            "integration_id": INTEGRATION_ID,
            "provider_slug": "conta-azul",
            "redirect_uri": "https://api.uuba.tech/oauth/callback",
        },
        headers=AUTH,
    )
    state_token = resp.json()["state_token"]

    # Poll
    resp = await client.get(
        f"/api/v1/integrations/oauth/state/{state_token}",
        headers=AUTH,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "pending"
    assert data["integration_id"] == INTEGRATION_ID


@pytest.mark.asyncio
async def test_poll_state_expired(client, seed_oauth_provider):
    """Criar state com expires_at no passado, GET retorna expired."""
    # Criar state expirado diretamente no DB
    async with seed_oauth_provider() as session:
        state = OAuthStateToken.generate_state()
        token = OAuthStateToken(
            id=generate_id("ost"),
            state_token=state,
            integration_id=INTEGRATION_ID,
            provider_slug="conta-azul",
            redirect_uri="https://api.uuba.tech/oauth/callback",
            status="pending",
            expires_at=datetime.now(timezone.utc) - timedelta(minutes=5),
            created_at=datetime.now(timezone.utc) - timedelta(minutes=65),
        )
        session.add(token)
        await session.commit()

    # Poll
    resp = await client.get(
        f"/api/v1/integrations/oauth/state/{state}",
        headers=AUTH,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "expired"


@pytest.mark.asyncio
async def test_callback_invalid_state(client, engine):
    """GET /oauth/callback?state=invalid retorna 400."""
    resp = await client.get(
        "/oauth/callback",
        params={"code": "authcode123", "state": "invalid_state_token"},
    )
    assert resp.status_code == 400
    assert "inválido" in resp.text.lower() or "inv" in resp.text.lower()


@pytest.mark.asyncio
async def test_callback_expired_state(client, seed_oauth_provider):
    """Criar state expirado, callback retorna 400."""
    async with seed_oauth_provider() as session:
        state = OAuthStateToken.generate_state()
        token = OAuthStateToken(
            id=generate_id("ost"),
            state_token=state,
            integration_id=INTEGRATION_ID,
            provider_slug="conta-azul",
            redirect_uri="https://api.uuba.tech/oauth/callback",
            status="pending",
            expires_at=datetime.now(timezone.utc) - timedelta(minutes=5),
            created_at=datetime.now(timezone.utc) - timedelta(minutes=65),
        )
        session.add(token)
        await session.commit()

    resp = await client.get(
        "/oauth/callback",
        params={"code": "authcode123", "state": state},
    )
    assert resp.status_code == 400
    assert "expirado" in resp.text.lower()


@pytest.mark.asyncio
async def test_create_state_no_auth(client, engine):
    """POST sem API key retorna 401."""
    resp = await client.post(
        "/api/v1/integrations/oauth/state",
        json={
            "integration_id": "int_xxx",
            "provider_slug": "conta-azul",
            "redirect_uri": "https://api.uuba.tech/oauth/callback",
        },
        # sem AUTH header
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
@pytest.mark.skip(reason="requires httpx mock for token exchange")
async def test_callback_happy_path(client, seed_oauth_provider):
    """Callback happy path — troca code por tokens e salva no cofre."""
    pass
