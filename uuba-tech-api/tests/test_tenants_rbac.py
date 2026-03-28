"""Tests for RBAC on tenants endpoints — POST/PATCH require tenants:write."""

import os

os.environ["TESTING"] = "1"

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.auth.api_key import clear_tenant_cache, verify_api_key
from app.config import settings
from app.database import get_db
from app.exceptions import APIError
from app.main import app
from app.models.audit_log import AuditLog  # noqa: F401
from app.models.base import Base
from app.models.regua import Regua, ReguaPasso  # noqa: F401
from app.models.tenant import Tenant
from fastapi import Request

TEST_TENANT_ID = "ten_test"
API_KEY = settings.api_key
AUTH = {"X-API-Key": API_KEY}
ADMIN_KEY = "admin-test-key-rbac"
ADMIN_AUTH = {"X-API-Key": ADMIN_KEY}


@pytest.fixture
async def engine():
    _engine = create_async_engine(
        "sqlite+aiosqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(_engine.sync_engine, "connect")
    def enable_fk(dbapi_conn, _):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(_engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        session.add(
            Tenant(
                id=TEST_TENANT_ID,
                nome="Tenant Teste",
                slug="tenant-teste",
                documento="00000000000100",
                api_key=API_KEY,
                ativo=True,
                plan="starter",
            )
        )
        session.add(
            Tenant(
                id="ten_admin",
                nome="Admin Tenant",
                slug="admin-tenant",
                documento="11111111000111",
                api_key=ADMIN_KEY,
                ativo=True,
                plan="enterprise",
            )
        )
        await session.commit()

    yield _engine

    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await _engine.dispose()


@pytest.fixture
async def client(engine):
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db():
        async with factory() as session:
            yield session

    async def override_verify(request: Request):
        key = request.headers.get("X-API-Key", "")
        if not key:
            raise APIError(401, "auth-invalida", "Autenticacao invalida", "API key ausente")
        if key == ADMIN_KEY:
            request.state.tenant_id = "ten_admin"
            request.state.permissions = ["tenants:write", "tenants:read"]
            request.state.key_id = "key_admin"
        else:
            request.state.tenant_id = TEST_TENANT_ID
            request.state.permissions = []
            request.state.key_id = "key_regular"
        return key

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[verify_api_key] = override_verify
    clear_tenant_cache()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


class TestTenantRBACWrite:
    """POST and PATCH require tenants:write permission."""

    async def test_post_without_permission_returns_403(self, client):
        resp = await client.post(
            "/api/v1/tenants",
            json={"name": "Novo Tenant"},
            headers=AUTH,
        )
        assert resp.status_code == 403
        assert "permissao-negada" in resp.json()["type"]

    async def test_patch_without_permission_returns_403(self, client):
        resp = await client.patch(
            f"/api/v1/tenants/{TEST_TENANT_ID}",
            json={"name": "Updated"},
            headers=AUTH,
        )
        assert resp.status_code == 403

    async def test_post_with_admin_returns_201(self, client):
        resp = await client.post(
            "/api/v1/tenants",
            json={"name": "Admin Created"},
            headers=ADMIN_AUTH,
        )
        assert resp.status_code == 201

    async def test_patch_with_admin_returns_200(self, client):
        resp = await client.patch(
            f"/api/v1/tenants/{TEST_TENANT_ID}",
            json={"name": "Admin Updated"},
            headers=ADMIN_AUTH,
        )
        assert resp.status_code == 200


class TestTenantRBACRead:
    """GET endpoints accessible to any authenticated key."""

    async def test_get_list_without_write_returns_200(self, client):
        resp = await client.get("/api/v1/tenants", headers=AUTH)
        assert resp.status_code == 200

    async def test_get_detail_without_write_returns_200(self, client):
        resp = await client.get(f"/api/v1/tenants/{TEST_TENANT_ID}", headers=AUTH)
        assert resp.status_code == 200

    async def test_no_api_key_returns_401(self, client):
        resp = await client.post(
            "/api/v1/tenants",
            json={"name": "No Key"},
        )
        assert resp.status_code == 401
