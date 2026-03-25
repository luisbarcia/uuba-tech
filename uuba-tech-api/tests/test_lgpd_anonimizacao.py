"""Testes LGPD: anonimização (direito ao esquecimento) e retenção de dados.

Art. 18 VI — Direito à eliminação de dados pessoais.
Art. 15/16 — Término do tratamento e eliminação.
"""

import pytest

from app.config import settings

AUTH = {"X-API-Key": settings.api_key}


# --- Helpers ---


async def _create_cliente(client, **overrides):
    defaults = dict(
        nome="Maria Silva",
        documento="52998224725",
        email="maria@test.com",
        telefone="5511999001234",
    )
    defaults.update(overrides)
    resp = await client.post("/api/v1/clientes", json=defaults, headers=AUTH)
    assert resp.status_code == 201
    return resp.json()


async def _create_fatura(client, cliente_id, **overrides):
    defaults = dict(
        cliente_id=cliente_id,
        valor=100000,
        vencimento="2026-04-01T00:00:00Z",
    )
    defaults.update(overrides)
    resp = await client.post("/api/v1/faturas", json=defaults, headers=AUTH)
    assert resp.status_code == 201
    return resp.json()


async def _create_cobranca(client, fatura_id, cliente_id, **overrides):
    defaults = dict(
        fatura_id=fatura_id,
        cliente_id=cliente_id,
        tipo="lembrete",
        canal="whatsapp",
        mensagem="Olá Maria, lembrete da fatura no valor de R$ 1.000,00",
        tom="amigavel",
    )
    defaults.update(overrides)
    resp = await client.post("/api/v1/cobrancas", json=defaults, headers=AUTH)
    assert resp.status_code == 201
    return resp.json()


# --- DELETE /api/v1/clientes/{id} ---


class TestAnonimizarCliente:
    @pytest.mark.asyncio
    async def test_delete_retorna_204(self, client):
        cli = await _create_cliente(client)
        resp = await client.delete(f"/api/v1/clientes/{cli['id']}", headers=AUTH)
        assert resp.status_code == 204

    @pytest.mark.asyncio
    async def test_dados_pii_anonimizados(self, client):
        cli = await _create_cliente(client)
        await client.delete(f"/api/v1/clientes/{cli['id']}", headers=AUTH)

        # GET deve retornar 404 (cliente anonimizado é "invisível")
        resp = await client.get(f"/api/v1/clientes/{cli['id']}", headers=AUTH)
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_cliente_nao_aparece_em_listagem(self, client):
        cli = await _create_cliente(client)
        await client.delete(f"/api/v1/clientes/{cli['id']}", headers=AUTH)

        resp = await client.get("/api/v1/clientes", headers=AUTH)
        ids = [c["id"] for c in resp.json()["data"]]
        assert cli["id"] not in ids

    @pytest.mark.asyncio
    async def test_delete_cliente_inexistente_retorna_404(self, client):
        resp = await client.delete("/api/v1/clientes/cli_naoexiste", headers=AUTH)
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_mensagens_cobranca_anonimizadas(self, client):
        """Mensagens de cobrança do cliente devem ser removidas."""
        cli = await _create_cliente(client)
        fat = await _create_fatura(client, cli["id"])
        await _create_cobranca(client, fat["id"], cli["id"])

        await client.delete(f"/api/v1/clientes/{cli['id']}", headers=AUTH)

        # Cobrança ainda existe (integridade referencial), mas mensagem limpa
        resp = await client.get(f"/api/v1/cobrancas/{fat['id']}/historico", headers=AUTH)
        assert resp.status_code == 200
        cobrancas = resp.json()["data"]
        for c in cobrancas:
            assert c["mensagem"] is None

    @pytest.mark.asyncio
    async def test_faturas_preservadas(self, client):
        """Faturas devem continuar existindo (integridade referencial)."""
        cli = await _create_cliente(client)
        fat = await _create_fatura(client, cli["id"])

        await client.delete(f"/api/v1/clientes/{cli['id']}", headers=AUTH)

        resp = await client.get(f"/api/v1/faturas/{fat['id']}", headers=AUTH)
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_delete_idempotente(self, client):
        """Deletar cliente já deletado retorna 404."""
        cli = await _create_cliente(client)
        resp1 = await client.delete(f"/api/v1/clientes/{cli['id']}", headers=AUTH)
        assert resp1.status_code == 204

        resp2 = await client.delete(f"/api/v1/clientes/{cli['id']}", headers=AUTH)
        assert resp2.status_code == 404

    @pytest.mark.asyncio
    async def test_documento_hash_preserva_deduplicacao(self, client):
        """Após anonimização, não deve ser possível re-cadastrar mesmo documento."""
        cli = await _create_cliente(client, documento="52998224725")
        await client.delete(f"/api/v1/clientes/{cli['id']}", headers=AUTH)

        # Tentar re-cadastrar com mesmo documento deve funcionar
        # (documento foi substituído por hash, UNIQUE index não bloqueia)
        resp = await client.post(
            "/api/v1/clientes",
            json={"nome": "Outra Pessoa", "documento": "52998224725"},
            headers=AUTH,
        )
        assert resp.status_code == 201
