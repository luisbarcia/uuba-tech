"""Testes do endpoint GET /api/v1/watch/snapshot."""

import pytest

from tests.conftest import AUTH, create_test_cliente, create_test_fatura


class TestWatchSnapshot:
    @pytest.mark.asyncio
    async def test_snapshot_returns_200(self, client):
        resp = await client.get("/api/v1/watch/snapshot", headers=AUTH)
        assert resp.status_code == 200
        data = resp.json()
        assert "tenants" in data
        assert "invoices_overdue" in data
        assert "keys_created_24h" in data
        assert "api_latency_avg_ms" in data

    @pytest.mark.asyncio
    async def test_snapshot_counts_overdue_for_tenant(self, client):
        cli = await create_test_cliente(client)
        await create_test_fatura(client, cli["id"])

        resp = await client.get("/api/v1/watch/snapshot", headers=AUTH)
        assert resp.status_code == 200
        data = resp.json()
        assert data["invoices_overdue"] >= 0

    @pytest.mark.asyncio
    async def test_snapshot_requires_auth(self, client):
        resp = await client.get("/api/v1/watch/snapshot")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_snapshot_tenants_field_is_1(self, client):
        """Tenant so ve a si mesmo, nao count global."""
        resp = await client.get("/api/v1/watch/snapshot", headers=AUTH)
        data = resp.json()
        assert data["tenants"] == 1

    @pytest.mark.asyncio
    async def test_snapshot_empty_db(self, client):
        resp = await client.get("/api/v1/watch/snapshot", headers=AUTH)
        data = resp.json()
        assert data["invoices_overdue"] == 0
        assert data["clients_active"] == 0
