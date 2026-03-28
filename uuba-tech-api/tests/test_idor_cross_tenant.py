"""Testes IDOR (Insecure Direct Object Reference) cross-tenant.

Verifica que tenant A NAO consegue acessar, modificar ou deletar
recursos de tenant B usando o ID direto do recurso.

Complementa test_multi_tenant_isolation.py que cobre GET e LIST.
Estes testes cobrem: PATCH, DELETE, POST anonimizar, exportar,
metricas, cobrancas (pausar/retomar/historico).
"""

import pytest

from tests.test_multi_tenant_isolation import AUTH_A, AUTH_B
from tests.test_multi_tenant_isolation import two_tenant_client as two_tenant_client  # noqa: F811


async def _create_full_stack(client, auth):
    """Helper: cria cliente + fatura + cobranca para um tenant."""
    cli = await client.post(
        "/api/v1/clientes",
        json={"nome": "IDOR Test", "documento": "52998224725"},
        headers=auth,
    )
    cli_id = cli.json()["id"]

    fat = await client.post(
        "/api/v1/faturas",
        json={
            "cliente_id": cli_id,
            "valor": 100000,
            "vencimento": "2026-06-01T00:00:00Z",
        },
        headers=auth,
    )
    fat_id = fat.json()["id"]

    cob = await client.post(
        "/api/v1/cobrancas",
        json={
            "fatura_id": fat_id,
            "cliente_id": cli_id,
            "tipo": "lembrete",
            "canal": "whatsapp",
        },
        headers=auth,
    )
    cob_id = cob.json()["id"]

    return cli_id, fat_id, cob_id


# --- PATCH cross-tenant ---


class TestIDORPatch:
    @pytest.mark.asyncio
    async def test_patch_cliente_de_outro_tenant_404(self, two_tenant_client):
        c = two_tenant_client
        cli_a, _, _ = await _create_full_stack(c, AUTH_A)

        resp = await c.patch(
            f"/api/v1/clientes/{cli_a}",
            json={"nome": "Hackeado"},
            headers=AUTH_B,
        )
        assert resp.status_code == 404

        # Confirma que nome NAO mudou
        resp_check = await c.get(f"/api/v1/clientes/{cli_a}", headers=AUTH_A)
        assert resp_check.json()["nome"] == "IDOR Test"

    @pytest.mark.asyncio
    async def test_patch_fatura_de_outro_tenant_404(self, two_tenant_client):
        c = two_tenant_client
        _, fat_a, _ = await _create_full_stack(c, AUTH_A)

        resp = await c.patch(
            f"/api/v1/faturas/{fat_a}",
            json={"status": "cancelado"},
            headers=AUTH_B,
        )
        assert resp.status_code == 404

        # Confirma que status NAO mudou
        resp_check = await c.get(f"/api/v1/faturas/{fat_a}", headers=AUTH_A)
        assert resp_check.json()["status"] == "pendente"


# --- DELETE / Anonimizar cross-tenant ---


class TestIDORDelete:
    @pytest.mark.asyncio
    async def test_delete_cliente_de_outro_tenant_404(self, two_tenant_client):
        c = two_tenant_client
        cli_a, _, _ = await _create_full_stack(c, AUTH_A)

        resp = await c.delete(f"/api/v1/clientes/{cli_a}", headers=AUTH_B)
        assert resp.status_code == 404

        # Confirma que cliente A continua vivo
        resp_check = await c.get(f"/api/v1/clientes/{cli_a}", headers=AUTH_A)
        assert resp_check.status_code == 200

    @pytest.mark.asyncio
    async def test_anonimizar_cliente_de_outro_tenant_404(self, two_tenant_client):
        c = two_tenant_client
        cli_a, _, _ = await _create_full_stack(c, AUTH_A)

        resp = await c.post(
            f"/api/v1/clientes/{cli_a}/anonimizar",
            headers=AUTH_B,
        )
        assert resp.status_code == 404

        # Confirma que cliente A NAO foi anonimizado
        resp_check = await c.get(f"/api/v1/clientes/{cli_a}", headers=AUTH_A)
        assert resp_check.json()["nome"] == "IDOR Test"


# --- Exportar / Dados Pessoais cross-tenant ---


class TestIDORExportar:
    @pytest.mark.asyncio
    async def test_exportar_cliente_de_outro_tenant_404(self, two_tenant_client):
        c = two_tenant_client
        cli_a, _, _ = await _create_full_stack(c, AUTH_A)

        resp = await c.get(
            f"/api/v1/clientes/{cli_a}/exportar",
            headers=AUTH_B,
        )
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_metricas_cliente_de_outro_tenant_404(self, two_tenant_client):
        c = two_tenant_client
        cli_a, _, _ = await _create_full_stack(c, AUTH_A)

        resp = await c.get(
            f"/api/v1/clientes/{cli_a}/metricas",
            headers=AUTH_B,
        )
        assert resp.status_code == 404


# --- Cobrancas cross-tenant ---


class TestIDORCobrancas:
    @pytest.mark.asyncio
    async def test_pausar_cobranca_de_outro_tenant_404(self, two_tenant_client):
        c = two_tenant_client
        _, _, cob_a = await _create_full_stack(c, AUTH_A)

        resp = await c.patch(
            f"/api/v1/cobrancas/{cob_a}/pausar",
            headers=AUTH_B,
        )
        assert resp.status_code == 404

        # Confirma que cobranca A NAO foi pausada
        resp_list = await c.get("/api/v1/cobrancas", headers=AUTH_A)
        for cob in resp_list.json()["data"]:
            if cob["id"] == cob_a:
                assert cob["pausado"] is False

    @pytest.mark.asyncio
    async def test_retomar_cobranca_de_outro_tenant_404(self, two_tenant_client):
        c = two_tenant_client
        _, _, cob_a = await _create_full_stack(c, AUTH_A)

        # Primeiro pausa com auth correta
        await c.patch(f"/api/v1/cobrancas/{cob_a}/pausar", headers=AUTH_A)

        # Tenant B tenta retomar
        resp = await c.patch(
            f"/api/v1/cobrancas/{cob_a}/retomar",
            headers=AUTH_B,
        )
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_historico_fatura_de_outro_tenant_vazio(self, two_tenant_client):
        """Historico de cobrancas de fatura de outro tenant retorna lista vazia."""
        c = two_tenant_client
        _, fat_a, _ = await _create_full_stack(c, AUTH_A)

        resp = await c.get(
            f"/api/v1/cobrancas/{fat_a}/historico",
            headers=AUTH_B,
        )
        assert resp.status_code == 200
        assert resp.json()["pagination"]["total"] == 0


# --- Busca cross-tenant ---


class TestIDORBusca:
    @pytest.mark.asyncio
    async def test_busca_nao_retorna_clientes_de_outro_tenant(self, two_tenant_client):
        c = two_tenant_client
        await _create_full_stack(c, AUTH_A)

        resp = await c.get(
            "/api/v1/clientes/busca?q=IDOR",
            headers=AUTH_B,
        )
        assert resp.status_code == 200
        assert resp.json()["pagination"]["total"] == 0
