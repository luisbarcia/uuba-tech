"""Testes do endpoint de metricas agregadas (GET /api/v1/metricas)."""

import pytest

from tests.conftest import AUTH, create_test_cliente, create_test_fatura


class TestMetricasAgregadas:
    @pytest.mark.asyncio
    async def test_metricas_returns_200(self, client):
        resp = await client.get("/api/v1/metricas", headers=AUTH)
        assert resp.status_code == 200
        body = resp.json()
        assert "dso" in body
        assert "revenue_monthly_cents" in body
        assert "revenue_accumulated_cents" in body
        assert "overdue_count" in body
        assert "overdue_total_cents" in body
        assert "clients_active" in body
        assert "clients_inactive" in body

    @pytest.mark.asyncio
    async def test_metricas_empty_db(self, client):
        resp = await client.get("/api/v1/metricas", headers=AUTH)
        body = resp.json()
        assert body["dso"] == 0.0
        assert body["revenue_monthly_cents"] == 0
        assert body["overdue_count"] == 0
        assert body["clients_active"] == 0

    @pytest.mark.asyncio
    async def test_metricas_with_clients(self, client):
        await create_test_cliente(client, documento="11111111000111")
        await create_test_cliente(client, nome="Loja B", documento="22222222000122")

        resp = await client.get("/api/v1/metricas", headers=AUTH)
        body = resp.json()
        assert body["clients_active"] == 2
        assert body["clients_inactive"] == 0

    @pytest.mark.asyncio
    async def test_metricas_with_faturas(self, client):
        cli = await create_test_cliente(client)
        await create_test_fatura(client, cli["id"], valor=100000)

        resp = await client.get("/api/v1/metricas", headers=AUTH)
        body = resp.json()
        assert body["clients_active"] >= 1

    @pytest.mark.asyncio
    async def test_metricas_requires_auth(self, client):
        resp = await client.get("/api/v1/metricas")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_metricas_ignora_query_param_tenant_id(self, client):
        """Apos fix BUG-001: tenant_id query param foi removido.
        O endpoint usa request.state.tenant_id do auth."""
        resp = await client.get(
            "/api/v1/metricas?tenant_id=ten_nonexistent",
            headers=AUTH,
        )
        # Query param desconhecido e ignorado pelo FastAPI (nao causa erro)
        assert resp.status_code == 200
