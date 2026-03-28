"""Testes do endpoint GET /api/v1/usage."""

import pytest

from tests.conftest import AUTH


class TestUsage:
    @pytest.mark.asyncio
    async def test_usage_returns_200(self, client):
        resp = await client.get("/api/v1/usage", headers=AUTH)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    @pytest.mark.asyncio
    async def test_usage_requires_auth(self, client):
        resp = await client.get("/api/v1/usage")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_usage_default_30_days(self, client):
        resp = await client.get("/api/v1/usage", headers=AUTH)
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_usage_custom_days(self, client):
        resp = await client.get("/api/v1/usage?days=7", headers=AUTH)
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_usage_invalid_days(self, client):
        resp = await client.get("/api/v1/usage?days=0", headers=AUTH)
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_usage_days_too_large(self, client):
        resp = await client.get("/api/v1/usage?days=999", headers=AUTH)
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_usage_no_tenant_id_override(self, client):
        """Nao deve aceitar tenant_id como query param (IDOR fix)."""
        resp = await client.get("/api/v1/usage?tenant_id=ten_other", headers=AUTH)
        # O param eh ignorado (nao existe mais), request deve funcionar normalmente
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_usage_empty_db(self, client):
        resp = await client.get("/api/v1/usage", headers=AUTH)
        assert resp.status_code == 200
        assert resp.json() == []
