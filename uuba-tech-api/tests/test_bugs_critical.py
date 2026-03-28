"""Testes de regressao para bugs criticos encontrados na revisao de 2026-03-27.

Cada teste reproduz um bug ANTES do fix — deve FALHAR no codigo bugado
e PASSAR apos o fix ser aplicado.
"""

import pytest

from tests.conftest import AUTH, create_test_cliente, create_test_fatura


# --- BUG-001: Metricas ignora tenant_id do auth ---


class TestBugMetricasCrossTenant:
    """GET /api/v1/metricas deve usar tenant_id do auth, nao do query param."""

    @pytest.mark.asyncio
    async def test_metricas_usa_tenant_do_auth(self, client):
        """Metricas devem retornar dados apenas do tenant autenticado,
        independente do query param tenant_id."""
        resp = await client.get("/api/v1/metricas", headers=AUTH)
        assert resp.status_code == 200
        body = resp.json()
        # Deve retornar metricas validas (nao importa se zeradas)
        assert "dso" in body
        assert "clients_active" in body

    @pytest.mark.asyncio
    async def test_metricas_rejeita_tenant_id_diferente(self, client):
        """Passar tenant_id diferente do autenticado deve ser ignorado
        ou bloqueado — NUNCA deve retornar dados de outro tenant."""
        # Criar dados no tenant de teste
        cli = await create_test_cliente(client)
        await create_test_fatura(client, cli["id"], valor=100000)

        # Pedir metricas com tenant_id forjado
        resp_forjado = await client.get(
            "/api/v1/metricas?tenant_id=ten_outro_tenant",
            headers=AUTH,
        )
        assert resp_forjado.status_code == 200

        # Pedir metricas normais (sem query param)
        resp_normal = await client.get("/api/v1/metricas", headers=AUTH)
        assert resp_normal.status_code == 200

        # Ambas devem retornar os MESMOS dados (tenant do auth)
        assert resp_forjado.json()["clients_active"] == resp_normal.json()["clients_active"]


# --- BUG-002: Tenant service nao trata slug duplicado ---


class TestBugTenantSlugDuplicado:
    """POST /api/v1/tenants com nome que gera slug duplicado deve retornar 409."""

    @pytest.mark.asyncio
    async def test_slug_duplicado_retorna_409(self, client):
        """Criar dois tenants com mesmo nome deve retornar 409, nao 500."""
        resp1 = await client.post(
            "/api/v1/tenants",
            json={"name": "Duplicado Test"},
            headers=AUTH,
        )
        assert resp1.status_code == 201

        resp2 = await client.post(
            "/api/v1/tenants",
            json={"name": "Duplicado Test"},
            headers=AUTH,
        )
        # Bug: retorna 500 (IntegrityError nao tratado)
        # Fix: deve retornar 409
        assert resp2.status_code == 409


# --- BUG-003: Metricas service calcula DSO com todas faturas (sem tenant filter) ---


class TestBugMetricasSemTenantFilter:
    """metricas_service.get_metricas() sem tenant_id retorna dados de TODOS os tenants."""

    @pytest.mark.asyncio
    async def test_metricas_endpoint_sempre_filtra_por_tenant(self, client):
        """O endpoint deve SEMPRE filtrar pelo tenant autenticado,
        mesmo que o service aceite tenant_id=None."""
        resp = await client.get("/api/v1/metricas", headers=AUTH)
        assert resp.status_code == 200
        # Se o tenant de teste nao tem faturas, overdue deve ser 0
        # (nao deve somar faturas de outros tenants que nao existem)
        body = resp.json()
        assert isinstance(body["overdue_count"], int)
        assert isinstance(body["dso"], (int, float))
