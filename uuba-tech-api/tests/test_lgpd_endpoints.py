"""Testes LGPD: endpoints de privacidade, portabilidade, audit trail, rate limiting, mascaramento."""

import pytest

from app.config import settings

AUTH = {"X-API-Key": settings.api_key}


async def _create_cliente(client, **overrides):
    defaults = dict(nome="Maria Silva", documento="52998224725")
    defaults.update(overrides)
    resp = await client.post("/api/v1/clientes", json=defaults, headers=AUTH)
    assert resp.status_code == 201
    return resp.json()


async def _create_fatura(client, cliente_id):
    resp = await client.post(
        "/api/v1/faturas",
        json={"cliente_id": cliente_id, "valor": 100000, "vencimento": "2026-04-01T00:00:00Z"},
        headers=AUTH,
    )
    assert resp.status_code == 201
    return resp.json()


# --- GET /api/v1/privacidade (público) ---


class TestAvisoPrivacidade:
    @pytest.mark.asyncio
    async def test_retorna_200_sem_auth(self, client):
        resp = await client.get("/api/v1/privacidade")
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_contem_campos_obrigatorios(self, client):
        data = (await client.get("/api/v1/privacidade")).json()
        assert "controlador" in data
        assert "dados_coletados" in data
        assert "direitos_titular" in data
        assert "retencao" in data
        assert "como_exercer_direitos" in data


# --- GET /api/v1/clientes/{id}/dados-pessoais ---


class TestDadosPessoais:
    @pytest.mark.asyncio
    async def test_retorna_dados_completos(self, client):
        cli = await _create_cliente(client)
        await _create_fatura(client, cli["id"])

        resp = await client.get(f"/api/v1/clientes/{cli['id']}/dados-pessoais", headers=AUTH)
        assert resp.status_code == 200
        data = resp.json()
        assert data["titular"]["nome"] == "Maria Silva"
        assert data["titular"]["documento"] == "52998224725"
        assert len(data["faturas"]) == 1
        assert "exportado_em" in data
        assert "lgpd" in data

    @pytest.mark.asyncio
    async def test_cliente_inexistente_404(self, client):
        resp = await client.get("/api/v1/clientes/cli_naoexiste/dados-pessoais", headers=AUTH)
        assert resp.status_code == 404


# --- GET /admin/audit ---


class TestAuditTrail:
    @pytest.mark.asyncio
    async def test_audit_retorna_lista(self, client):
        resp = await client.get("/api/v1/admin/audit", headers=AUTH)
        assert resp.status_code == 200
        assert "data" in resp.json()
        assert "pagination" in resp.json()


# --- Mascaramento de documento em listagem ---


class TestMascaramentoDocumento:
    @pytest.mark.asyncio
    async def test_listagem_mascara_cpf(self, client):
        await _create_cliente(client, documento="52998224725")
        resp = await client.get("/api/v1/clientes", headers=AUTH)
        item = resp.json()["data"][0]
        assert "documento_mascarado" in item
        assert "documento" not in item
        # CPF mascarado: ***.982.***-25
        assert item["documento_mascarado"].startswith("***.")
        assert item["documento_mascarado"].endswith("-25")

    @pytest.mark.asyncio
    async def test_detalhe_retorna_documento_completo(self, client):
        cli = await _create_cliente(client, documento="52998224725")
        resp = await client.get(f"/api/v1/clientes/{cli['id']}", headers=AUTH)
        data = resp.json()
        assert data["documento"] == "52998224725"
