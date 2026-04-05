"""Testes de isolamento BOLA (Broken Object Level Authorization) para webhooks.

Garante que Tenant A NAO pode ver, testar ou deletar webhooks de Tenant B.
Reutiliza a fixture two_tenant_client do test_multi_tenant_isolation.
"""

from unittest.mock import patch

import pytest

from tests.test_multi_tenant_isolation import AUTH_A, AUTH_B
from tests.test_multi_tenant_isolation import two_tenant_client as two_tenant_client  # noqa: F401


def _mock_dns_public():
    """Context manager que mocka DNS para retornar IP publico."""
    fake_addrinfo = [(2, 1, 6, "", ("93.184.216.34", 0))]
    return patch("app.routers.webhooks.socket.getaddrinfo", return_value=fake_addrinfo)


async def _create_webhook(client, auth, url="https://example.com/hook"):
    """Helper para criar webhook com DNS mockado."""
    with _mock_dns_public():
        resp = await client.post(
            "/api/v1/webhooks",
            json={"url": url, "events": ["invoice.paid"]},
            headers=auth,
        )
    assert resp.status_code == 201, f"Falha ao criar webhook: {resp.text}"
    return resp.json()


class TestWebhookBOLAList:
    """Tenant A nao pode ver webhooks de Tenant B via GET."""

    @pytest.mark.asyncio
    async def test_tenant_a_nao_ve_webhooks_de_b(self, two_tenant_client):
        c = two_tenant_client

        # Tenant A cria webhook
        wh_a = await _create_webhook(c, AUTH_A, "https://a.example.com/hook")

        # Tenant B cria webhook
        wh_b = await _create_webhook(c, AUTH_B, "https://b.example.com/hook")

        # Tenant A lista: so ve o seu
        resp_a = await c.get("/api/v1/webhooks", headers=AUTH_A)
        assert resp_a.status_code == 200
        ids_a = [w["id"] for w in resp_a.json()]
        assert wh_a["id"] in ids_a
        assert wh_b["id"] not in ids_a

        # Tenant B lista: so ve o seu
        resp_b = await c.get("/api/v1/webhooks", headers=AUTH_B)
        assert resp_b.status_code == 200
        ids_b = [w["id"] for w in resp_b.json()]
        assert wh_b["id"] in ids_b
        assert wh_a["id"] not in ids_b

    @pytest.mark.asyncio
    async def test_list_empty_for_other_tenant(self, two_tenant_client):
        c = two_tenant_client

        # Apenas Tenant A cria webhook
        await _create_webhook(c, AUTH_A)

        # Tenant B lista: vazio
        resp_b = await c.get("/api/v1/webhooks", headers=AUTH_B)
        assert resp_b.status_code == 200
        assert resp_b.json() == []


class TestWebhookBOLATest:
    """Tenant A nao pode testar webhook de Tenant B via POST /{id}/test."""

    @pytest.mark.asyncio
    async def test_cross_tenant_test_returns_404(self, two_tenant_client):
        c = two_tenant_client

        # Tenant A cria webhook
        wh_a = await _create_webhook(c, AUTH_A)

        # Tenant B tenta testar webhook de A: 404
        resp = await c.post(f"/api/v1/webhooks/{wh_a['id']}/test", headers=AUTH_B)
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_own_tenant_test_succeeds(self, two_tenant_client):
        c = two_tenant_client

        # Tenant A cria e testa seu proprio webhook
        wh_a = await _create_webhook(c, AUTH_A)
        resp = await c.post(f"/api/v1/webhooks/{wh_a['id']}/test", headers=AUTH_A)
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"


class TestWebhookBOLADelete:
    """Tenant A nao pode deletar webhook de Tenant B via DELETE /{id}."""

    @pytest.mark.asyncio
    async def test_cross_tenant_delete_returns_404(self, two_tenant_client):
        c = two_tenant_client

        # Tenant A cria webhook
        wh_a = await _create_webhook(c, AUTH_A)

        # Tenant B tenta deletar webhook de A: 404
        resp = await c.delete(f"/api/v1/webhooks/{wh_a['id']}", headers=AUTH_B)
        assert resp.status_code == 404

        # Webhook de A continua existindo
        resp_list = await c.get("/api/v1/webhooks", headers=AUTH_A)
        ids = [w["id"] for w in resp_list.json()]
        assert wh_a["id"] in ids

    @pytest.mark.asyncio
    async def test_own_tenant_delete_succeeds(self, two_tenant_client):
        c = two_tenant_client

        # Tenant A cria e deleta seu proprio webhook
        wh_a = await _create_webhook(c, AUTH_A)
        resp = await c.delete(f"/api/v1/webhooks/{wh_a['id']}", headers=AUTH_A)
        assert resp.status_code == 204

        # Confirmacao: webhook nao aparece mais
        resp_list = await c.get("/api/v1/webhooks", headers=AUTH_A)
        ids = [w["id"] for w in resp_list.json()]
        assert wh_a["id"] not in ids
