"""Testes do endpoint GET /api/v1/clientes/{id}/exportar (LGPD Art. 18 — Portabilidade)."""

import pytest

from tests.conftest import AUTH, create_test_cliente, create_test_fatura, create_test_cobranca


class TestExportarCliente:
    @pytest.mark.asyncio
    async def test_exportar_returns_200(self, client):
        cli = await create_test_cliente(client)
        resp = await client.get(
            f"/api/v1/clientes/{cli['id']}/exportar",
            headers=AUTH,
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "cliente" in body
        assert "faturas" in body
        assert "cobrancas" in body
        assert "metricas" in body
        assert "exported_at" in body

    @pytest.mark.asyncio
    async def test_exportar_cliente_data(self, client):
        cli = await create_test_cliente(
            client,
            nome="Maria Export",
            documento="52998224725",
            email="maria@export.com",
        )
        resp = await client.get(
            f"/api/v1/clientes/{cli['id']}/exportar",
            headers=AUTH,
        )
        body = resp.json()
        assert body["cliente"]["nome"] == "Maria Export"
        assert body["cliente"]["documento"] == "52998224725"
        assert body["cliente"]["email"] == "maria@export.com"
        assert body["cliente"]["id"] == cli["id"]
        assert body["cliente"]["object"] == "cliente"

    @pytest.mark.asyncio
    async def test_exportar_with_faturas(self, client):
        cli = await create_test_cliente(client)
        fat = await create_test_fatura(client, cli["id"], valor=200000)

        resp = await client.get(
            f"/api/v1/clientes/{cli['id']}/exportar",
            headers=AUTH,
        )
        body = resp.json()
        assert len(body["faturas"]) == 1
        assert body["faturas"][0]["id"] == fat["id"]
        assert body["faturas"][0]["valor"] == 200000

    @pytest.mark.asyncio
    async def test_exportar_with_cobrancas(self, client):
        cli = await create_test_cliente(client)
        fat = await create_test_fatura(client, cli["id"])
        cob = await create_test_cobranca(client, fat["id"], cli["id"])

        resp = await client.get(
            f"/api/v1/clientes/{cli['id']}/exportar",
            headers=AUTH,
        )
        body = resp.json()
        assert len(body["cobrancas"]) == 1
        assert body["cobrancas"][0]["id"] == cob["id"]

    @pytest.mark.asyncio
    async def test_exportar_metricas(self, client):
        cli = await create_test_cliente(client)
        await create_test_fatura(client, cli["id"], valor=300000)

        resp = await client.get(
            f"/api/v1/clientes/{cli['id']}/exportar",
            headers=AUTH,
        )
        body = resp.json()
        assert "dso_dias" in body["metricas"]
        assert "total_em_aberto" in body["metricas"]
        assert "faturas_em_aberto" in body["metricas"]

    @pytest.mark.asyncio
    async def test_exportar_not_found(self, client):
        resp = await client.get(
            "/api/v1/clientes/cli_naoexiste00/exportar",
            headers=AUTH,
        )
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_exportar_requires_auth(self, client):
        resp = await client.get("/api/v1/clientes/cli_qualquer/exportar")
        assert resp.status_code == 401
