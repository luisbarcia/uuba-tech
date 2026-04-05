"""Negative RBAC tests: endpoints with require_permission must return 403 without permission.

Covers: jobs (admin:write), logs (admin:read), watch (admin:read), v0/faturas (receivables:write).
Admin endpoints already tested in test_admin_rbac.py.
"""

import os

os.environ["TESTING"] = "1"

import pytest
from httpx import ASGITransport, AsyncClient
from fastapi import Request

from app.auth.api_key import clear_tenant_cache, verify_api_key
from app.database import get_db
from app.exceptions import APIError
from app.main import app

NO_PERMS_KEY = "key-no-perms"
NO_PERMS_AUTH = {"X-API-Key": NO_PERMS_KEY}


@pytest.fixture
async def client():
    """Client with a key that has NO permissions."""

    async def override_get_db():
        yield None  # DB not needed for 403 tests

    async def override_verify(request: Request):
        key = request.headers.get("X-API-Key", "")
        if not key:
            raise APIError(401, "auth-invalida", "Autenticacao invalida", "API key ausente")
        request.state.tenant_id = "ten_test"
        request.state.permissions = []  # No permissions at all
        request.state.key_id = "key_noperms"
        return key

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[verify_api_key] = override_verify
    clear_tenant_cache()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
    clear_tenant_cache()


class TestJobsRequireAdminWrite:
    """POST /api/v1/jobs/* requires admin:write."""

    @pytest.mark.asyncio
    async def test_jobs_vencimento_without_permission_returns_403(self, client):
        resp = await client.post("/api/v1/jobs/vencimento", headers=NO_PERMS_AUTH)
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_jobs_cobranca_without_permission_returns_403(self, client):
        resp = await client.post("/api/v1/jobs/cobranca", headers=NO_PERMS_AUTH)
        assert resp.status_code == 403


class TestLogsRequireAdminRead:
    """GET /api/v1/logs/* requires admin:read."""

    @pytest.mark.asyncio
    async def test_logs_without_permission_returns_403(self, client):
        resp = await client.get("/api/v1/logs", headers=NO_PERMS_AUTH)
        assert resp.status_code == 403


class TestWatchRequireAdminRead:
    """GET /api/v1/watch requires admin:read."""

    @pytest.mark.asyncio
    async def test_watch_without_permission_returns_403(self, client):
        resp = await client.get("/api/v1/watch", headers=NO_PERMS_AUTH)
        assert resp.status_code == 403


class TestV0FaturasRequireReceivablesWrite:
    """POST /api/v0/faturas requires receivables:write."""

    @pytest.mark.asyncio
    async def test_v0_faturas_without_permission_returns_403(self, client):
        resp = await client.post(
            "/api/v0/faturas",
            headers=NO_PERMS_AUTH,
            json={"customer": {"name": "Test"}, "operations": [], "payment_method": "boleto"},
        )
        assert resp.status_code == 403
