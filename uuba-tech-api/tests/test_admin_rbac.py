"""Tests for RBAC on admin endpoints + tenant isolation on reset.

- POST /admin/seed, DELETE /admin/reset, POST /admin/reset,
  POST /admin/cleanup, POST /admin/seed-regua require admin:write.
- GET /admin/audit is accessible to any authenticated key.
- Reset only deletes the authenticated tenant's data.
"""

import os

os.environ["TESTING"] = "1"

from datetime import datetime, timezone, timedelta

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event, select, func
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.auth.api_key import clear_tenant_cache, verify_api_key
from app.config import settings
from app.database import get_db
from app.exceptions import APIError
from app.main import app
from app.models.audit_log import AuditLog  # noqa: F401
from app.models.base import Base
from app.models.cliente import Cliente
from app.models.fatura import Fatura
from app.models.regua import Regua, ReguaPasso  # noqa: F401
from app.models.tenant import Tenant
from fastapi import Request

TENANT_A = "ten_a"
TENANT_B = "ten_b"
REGULAR_KEY = settings.api_key
ADMIN_KEY = "admin-key-rbac-test"
REGULAR_AUTH = {"X-API-Key": REGULAR_KEY}
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
                id=TENANT_A,
                nome="Tenant A",
                slug="tenant-a",
                documento="00000000000100",
                api_key=REGULAR_KEY,
                ativo=True,
                plan="starter",
            )
        )
        session.add(
            Tenant(
                id=TENANT_B,
                nome="Tenant B",
                slug="tenant-b",
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
    """Client where REGULAR_KEY has NO admin:write, ADMIN_KEY has admin:write."""
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db():
        async with factory() as session:
            yield session

    async def override_verify(request: Request):
        key = request.headers.get("X-API-Key", "")
        if not key:
            raise APIError(401, "auth-invalida", "Autenticacao invalida", "API key ausente")
        if key == ADMIN_KEY:
            request.state.tenant_id = TENANT_B
            request.state.permissions = ["admin:write", "tenants:write", "tenants:read"]
            request.state.key_id = "key_admin"
        elif key == REGULAR_KEY:
            request.state.tenant_id = TENANT_A
            request.state.permissions = []
            request.state.key_id = "key_regular"
        else:
            raise APIError(401, "auth-invalida", "Autenticacao invalida", "API key desconhecida")
        return key

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[verify_api_key] = override_verify
    clear_tenant_cache()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
    clear_tenant_cache()


# ---------------------------------------------------------------------------
# RBAC: endpoints that require admin:write
# ---------------------------------------------------------------------------


class TestAdminRBACWrite:
    """Destructive admin endpoints require admin:write permission."""

    @pytest.mark.asyncio
    async def test_seed_without_admin_write_returns_403(self, client):
        resp = await client.post("/api/v1/admin/seed", headers=REGULAR_AUTH)
        assert resp.status_code == 403
        assert "permissao-negada" in resp.json()["type"]

    @pytest.mark.asyncio
    async def test_reset_delete_without_admin_write_returns_403(self, client):
        resp = await client.delete(
            "/api/v1/admin/reset?confirm=delete-all-data",
            headers=REGULAR_AUTH,
        )
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_reset_post_without_admin_write_returns_403(self, client):
        resp = await client.post(
            "/api/v1/admin/reset?confirm=delete-all-data",
            headers=REGULAR_AUTH,
        )
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_cleanup_without_admin_write_returns_403(self, client):
        resp = await client.post("/api/v1/admin/cleanup", headers=REGULAR_AUTH)
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_seed_regua_without_admin_write_returns_403(self, client):
        resp = await client.post("/api/v1/admin/seed-regua", headers=REGULAR_AUTH)
        assert resp.status_code == 403


class TestAdminRBACRead:
    """GET /audit is accessible to any authenticated key."""

    @pytest.mark.asyncio
    async def test_audit_without_admin_write_returns_200(self, client):
        resp = await client.get("/api/v1/admin/audit", headers=REGULAR_AUTH)
        assert resp.status_code == 200


class TestAdminRBACWithPermission:
    """Admin operations succeed with admin:write permission."""

    @pytest.mark.asyncio
    async def test_seed_with_admin_write_works(self, client):
        resp = await client.post("/api/v1/admin/seed", headers=ADMIN_AUTH)
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"


# ---------------------------------------------------------------------------
# Multi-tenant isolation: reset only affects authenticated tenant
# ---------------------------------------------------------------------------


class TestResetTenantIsolation:
    """Reset must delete only the authenticated tenant's data."""

    @pytest.fixture
    async def seeded_engine(self, engine):
        """Seed data for both tenants directly in the DB."""
        factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        now = datetime.now(timezone.utc)
        vencimento = now + timedelta(days=30)

        async with factory() as session:
            # Tenant A data
            session.add(
                Cliente(
                    id="cli_a1",
                    tenant_id=TENANT_A,
                    nome="Cliente A",
                    documento="11111111111",
                )
            )
            await session.flush()
            session.add(
                Fatura(
                    id="fat_a1",
                    tenant_id=TENANT_A,
                    cliente_id="cli_a1",
                    valor=10000,
                    vencimento=vencimento,
                )
            )
            # Tenant B data
            session.add(
                Cliente(
                    id="cli_b1",
                    tenant_id=TENANT_B,
                    nome="Cliente B",
                    documento="22222222222",
                )
            )
            await session.flush()
            session.add(
                Fatura(
                    id="fat_b1",
                    tenant_id=TENANT_B,
                    cliente_id="cli_b1",
                    valor=20000,
                    vencimento=vencimento,
                )
            )
            await session.commit()

        return engine

    @pytest.fixture
    async def isolated_client(self, seeded_engine):
        """Client with seeded data for isolation test."""
        factory = async_sessionmaker(seeded_engine, class_=AsyncSession, expire_on_commit=False)

        async def override_get_db():
            async with factory() as session:
                yield session

        async def override_verify(request: Request):
            key = request.headers.get("X-API-Key", "")
            if not key:
                raise APIError(401, "auth-invalida", "Autenticacao invalida", "API key ausente")
            if key == ADMIN_KEY:
                request.state.tenant_id = TENANT_B
                request.state.permissions = [
                    "admin:write",
                    "tenants:write",
                    "tenants:read",
                ]
                request.state.key_id = "key_admin"
            elif key == REGULAR_KEY:
                request.state.tenant_id = TENANT_A
                request.state.permissions = ["admin:write"]
                request.state.key_id = "key_regular"
            else:
                raise APIError(
                    401, "auth-invalida", "Autenticacao invalida", "API key desconhecida"
                )
            return key

        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[verify_api_key] = override_verify
        clear_tenant_cache()

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            yield ac, factory

        app.dependency_overrides.clear()
        clear_tenant_cache()

    @pytest.mark.asyncio
    async def test_reset_only_deletes_own_tenant_data(self, isolated_client):
        ac, factory = isolated_client

        # Reset tenant A (REGULAR_KEY -> TENANT_A, has admin:write in this fixture)
        resp = await ac.delete(
            "/api/v1/admin/reset?confirm=delete-all-data",
            headers=REGULAR_AUTH,
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "ok"
        # Tenant A had 1 cliente + 1 fatura
        assert body["deleted"]["clientes"] == 1
        assert body["deleted"]["faturas"] == 1

        # Verify tenant B data is intact
        async with factory() as session:
            count_b_cli = await session.scalar(
                select(func.count()).select_from(Cliente).where(Cliente.tenant_id == TENANT_B)
            )
            count_b_fat = await session.scalar(
                select(func.count()).select_from(Fatura).where(Fatura.tenant_id == TENANT_B)
            )
            assert count_b_cli == 1, f"Tenant B clientes should be intact, got {count_b_cli}"
            assert count_b_fat == 1, f"Tenant B faturas should be intact, got {count_b_fat}"

        # Verify tenant A data is gone
        async with factory() as session:
            count_a_cli = await session.scalar(
                select(func.count()).select_from(Cliente).where(Cliente.tenant_id == TENANT_A)
            )
            assert count_a_cli == 0, f"Tenant A clientes should be 0, got {count_a_cli}"
