"""Testes dos filtros tenant_id em clientes, faturas e cobrancas.

Verifica que os query params tenant_id sao aceitos nos endpoints existentes.
"""

import pytest

from tests.conftest import AUTH


class TestClientesTenantFilter:
    @pytest.mark.asyncio
    async def test_list_clientes_accepts_tenant_id(self, client):
        resp = await client.get(
            "/api/v1/clientes?tenant_id=ten_qualquer",
            headers=AUTH,
        )
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_busca_accepts_tenant_id(self, client):
        resp = await client.get(
            "/api/v1/clientes/busca?q=teste&tenant_id=ten_qualquer",
            headers=AUTH,
        )
        assert resp.status_code == 200


class TestFaturasTenantFilter:
    @pytest.mark.asyncio
    async def test_list_faturas_accepts_tenant_id(self, client):
        resp = await client.get(
            "/api/v1/faturas?tenant_id=ten_qualquer",
            headers=AUTH,
        )
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_list_faturas_with_status_and_tenant(self, client):
        resp = await client.get(
            "/api/v1/faturas?status=pendente&tenant_id=ten_qualquer",
            headers=AUTH,
        )
        assert resp.status_code == 200


class TestCobrancasTenantFilter:
    @pytest.mark.asyncio
    async def test_list_cobrancas_accepts_tenant_id(self, client):
        resp = await client.get(
            "/api/v1/cobrancas?tenant_id=ten_qualquer",
            headers=AUTH,
        )
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_list_cobrancas_with_periodo_and_tenant(self, client):
        resp = await client.get(
            "/api/v1/cobrancas?periodo=7d&tenant_id=ten_qualquer",
            headers=AUTH,
        )
        assert resp.status_code == 200
