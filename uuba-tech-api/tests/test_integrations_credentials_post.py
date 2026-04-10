"""Testes para POST /api/v1/integrations/{integration_id}/credentials.

Valida: happy path, upsert, 404, 403 (wrong tenant), evento, 401.
"""

import os
import pytest
from datetime import datetime, timezone

from tests.conftest import AUTH, TEST_TENANT_ID
from app.models.integration import (
    IntegrationCredential,
    IntegrationEvent,
    IntegrationProvider,
    TenantIntegration,
)
from app.models.tenant import Tenant
from app.utils.ids import generate_id
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession


ENCRYPTION_KEY = "test_key_32_bytes_for_aes256_ok!"
PROVIDER_ID = "plat_pipedrive"
INTEGRATION_ID = "int_testcredpost"


@pytest.fixture(autouse=True)
def set_encryption_key():
    os.environ["UUBA_ENCRYPTION_KEY"] = ENCRYPTION_KEY
    yield
    os.environ.pop("UUBA_ENCRYPTION_KEY", None)


@pytest.fixture
async def seed_integration(engine):
    """Cria provider + integracao para testes."""
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        session.add(
            IntegrationProvider(
                id=PROVIDER_ID,
                slug="pipedrive",
                name="Pipedrive",
                category="crm",
                base_url="https://api.pipedrive.com/v1",
                is_active=True,
                created_at=datetime.now(timezone.utc),
            )
        )
        session.add(
            TenantIntegration(
                id=INTEGRATION_ID,
                tenant_id=TEST_TENANT_ID,
                provider_id=PROVIDER_ID,
                display_name="Producao",
                status="pending_setup",
                enabled=True,
            )
        )
        await session.commit()
    return factory


@pytest.mark.asyncio
async def test_set_credentials_happy_path(client, seed_integration):
    resp = await client.post(
        f"/api/v1/integrations/{INTEGRATION_ID}/credentials",
        json={"api_key": "sk_test_abc123"},
        headers=AUTH,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "ok"
    assert data["integration_id"] == INTEGRATION_ID
    assert "credential_id" in data

    # Verificar no DB
    async with seed_integration() as session:
        result = await session.execute(
            select(IntegrationCredential).where(
                IntegrationCredential.integration_id == INTEGRATION_ID
            )
        )
        cred = result.scalar_one_or_none()
        assert cred is not None
        assert len(cred.encrypted_data) > 0
        assert len(cred.iv) == 12


@pytest.mark.asyncio
async def test_set_credentials_updates_existing(client, seed_integration):
    # Primeiro POST
    resp1 = await client.post(
        f"/api/v1/integrations/{INTEGRATION_ID}/credentials",
        json={"api_key": "sk_first"},
        headers=AUTH,
    )
    assert resp1.status_code == 201
    cred_id_1 = resp1.json()["credential_id"]

    # Segundo POST — deve atualizar, nao duplicar
    resp2 = await client.post(
        f"/api/v1/integrations/{INTEGRATION_ID}/credentials",
        json={"api_key": "sk_second"},
        headers=AUTH,
    )
    assert resp2.status_code == 201
    cred_id_2 = resp2.json()["credential_id"]
    assert cred_id_1 == cred_id_2  # mesmo ID, atualizado

    # Verificar que so tem 1 credential
    async with seed_integration() as session:
        result = await session.execute(
            select(IntegrationCredential).where(
                IntegrationCredential.integration_id == INTEGRATION_ID
            )
        )
        creds = result.scalars().all()
        assert len(creds) == 1


@pytest.mark.asyncio
async def test_set_credentials_not_found(client, engine):
    resp = await client.post(
        "/api/v1/integrations/int_nonexistent/credentials",
        json={"api_key": "sk_test"},
        headers=AUTH,
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_set_credentials_wrong_tenant(client, engine):
    """Integration pertence a outro tenant — deve retornar 403."""
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        session.add(
            Tenant(
                id="ten_other",
                nome="Other Tenant",
                slug="other-tenant",
                documento="12345678000199",
                ativo=True,
                plan="starter",
            )
        )
        session.add(
            IntegrationProvider(
                id="plat_other",
                slug="other-provider",
                name="Other",
                category="test",
                is_active=True,
                created_at=datetime.now(timezone.utc),
            )
        )
        await session.flush()
        session.add(
            TenantIntegration(
                id="int_other_tenant",
                tenant_id="ten_other",
                provider_id="plat_other",
                display_name="Other",
                status="pending_setup",
                enabled=True,
            )
        )
        await session.commit()

    resp = await client.post(
        "/api/v1/integrations/int_other_tenant/credentials",
        json={"api_key": "sk_test"},
        headers=AUTH,
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_set_credentials_creates_event(client, seed_integration):
    await client.post(
        f"/api/v1/integrations/{INTEGRATION_ID}/credentials",
        json={"api_key": "sk_test"},
        headers=AUTH,
    )

    async with seed_integration() as session:
        result = await session.execute(
            select(IntegrationEvent).where(
                IntegrationEvent.integration_id == INTEGRATION_ID
            )
        )
        events = result.scalars().all()
        assert len(events) == 1
        assert events[0].event_type == "credentials_set"
        assert "api_key" in events[0].details["keys"]


@pytest.mark.asyncio
async def test_set_credentials_no_auth(client, engine):
    resp = await client.post(
        f"/api/v1/integrations/{INTEGRATION_ID}/credentials",
        json={"api_key": "sk_test"},
        # sem AUTH header
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_set_credentials_updates_status_from_pending(client, seed_integration):
    """Status muda de pending_setup para configuring apos salvar credenciais."""
    await client.post(
        f"/api/v1/integrations/{INTEGRATION_ID}/credentials",
        json={"api_key": "sk_test"},
        headers=AUTH,
    )

    async with seed_integration() as session:
        result = await session.execute(
            select(TenantIntegration).where(TenantIntegration.id == INTEGRATION_ID)
        )
        integration = result.scalar_one()
        assert integration.status == "configuring"
