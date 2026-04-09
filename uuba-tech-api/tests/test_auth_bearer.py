"""Testes para autenticacao via Authorization: Bearer header — TODOS os endpoints."""

import pytest

from tests.conftest import API_KEY, AUTH, BEARER_AUTH


@pytest.mark.asyncio
class TestBearerAuthAllEndpoints:
    """Bearer auth deve funcionar em TODOS os endpoints protegidos."""

    async def test_bearer_on_clientes_list(self, client):
        resp = await client.get("/api/v1/clientes", headers=BEARER_AUTH)
        assert resp.status_code == 200

    async def test_bearer_on_faturas_list(self, client):
        resp = await client.get("/api/v1/faturas", headers=BEARER_AUTH)
        assert resp.status_code == 200

    async def test_bearer_on_cobrancas_list(self, client):
        resp = await client.get("/api/v1/cobrancas", headers=BEARER_AUTH)
        assert resp.status_code == 200

    async def test_bearer_on_v0_faturas_dry_run(self, v0_client):
        payload = {
            "customer": {"type": "PJ", "document": "12345678000190", "name": "Teste Ltda"},
            "operations": [
                {
                    "service": {"code": "SVC-01", "description": "Teste"},
                    "sale": {"amount": 100.0, "due_date": "2026-12-01"},
                }
            ],
            "payment_method": "BOLETO_BANCARIO",
        }
        resp = await v0_client.post(
            "/api/v0/faturas?dry_run=true", json=payload, headers=BEARER_AUTH
        )
        assert resp.status_code == 200
        assert resp.json()["object"] == "validation_result"


@pytest.mark.asyncio
class TestXApiKeyBackwardCompat:
    """X-API-Key continua funcionando em todos os endpoints."""

    async def test_x_api_key_on_clientes(self, client):
        resp = await client.get("/api/v1/clientes", headers=AUTH)
        assert resp.status_code == 200

    async def test_x_api_key_on_faturas(self, client):
        resp = await client.get("/api/v1/faturas", headers=AUTH)
        assert resp.status_code == 200


@pytest.mark.asyncio
class TestBearerRejection:
    """Requests com Bearer malformado devem ser rejeitados."""

    async def test_empty_bearer_token(self, client):
        resp = await client.get("/api/v1/clientes", headers={"Authorization": "Bearer "})
        assert resp.status_code == 401

    async def test_wrong_bearer_token(self, client):
        resp = await client.get("/api/v1/clientes", headers={"Authorization": "Bearer wrong"})
        assert resp.status_code == 401

    async def test_no_bearer_prefix(self, client):
        resp = await client.get("/api/v1/clientes", headers={"Authorization": API_KEY})
        assert resp.status_code == 401

    async def test_basic_scheme_rejected(self, client):
        resp = await client.get(
            "/api/v1/clientes", headers={"Authorization": f"Basic {API_KEY}"}
        )
        assert resp.status_code == 401

    async def test_no_auth_at_all(self, client):
        resp = await client.get("/api/v1/clientes")
        assert resp.status_code == 401


@pytest.mark.asyncio
class TestBearerPriority:
    """Quando ambos headers presentes, Bearer tem prioridade."""

    async def test_valid_bearer_overrides_wrong_x_api_key(self, client):
        resp = await client.get(
            "/api/v1/clientes",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "X-API-Key": "wrong",
            },
        )
        assert resp.status_code == 200

    async def test_wrong_bearer_ignores_valid_x_api_key(self, client):
        resp = await client.get(
            "/api/v1/clientes",
            headers={
                "Authorization": "Bearer wrong",
                "X-API-Key": API_KEY,
            },
        )
        assert resp.status_code == 401
