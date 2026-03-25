"""Testes do motor da régua de cobrança.

Testa processamento de faturas vencidas, seleção de passo, compliance.
"""

import pytest

from app.config import settings

AUTH = {"X-API-Key": settings.api_key}


async def _create_cliente(client, **overrides):
    defaults = dict(nome="Devedor Teste", documento="52998224725")
    defaults.update(overrides)
    resp = await client.post("/api/v1/clientes", json=defaults, headers=AUTH)
    assert resp.status_code == 201
    return resp.json()


async def _create_fatura_vencida(client, cliente_id, **overrides):
    """Cria fatura já vencida (vencimento no passado) e transiciona para vencido."""
    defaults = dict(
        cliente_id=cliente_id,
        valor=250000,
        vencimento="2026-03-10T00:00:00Z",
        numero_nf="NF-TEST-001",
    )
    defaults.update(overrides)
    resp = await client.post("/api/v1/faturas", json=defaults, headers=AUTH)
    assert resp.status_code == 201
    fat = resp.json()

    # Transicionar para vencido
    resp2 = await client.patch(
        f"/api/v1/faturas/{fat['id']}",
        json={"status": "vencido"},
        headers=AUTH,
    )
    assert resp2.status_code == 200
    return resp2.json()


async def _seed_regua(client):
    """Cria régua padrão via seed."""
    resp = await client.post("/api/v1/admin/seed-regua", headers=AUTH)
    assert resp.status_code == 200
    return resp.json()


# --- POST /api/v1/jobs/processar-regua ---


class TestProcessarRegua:
    @pytest.mark.asyncio
    async def test_retorna_relatorio(self, client):
        await _seed_regua(client)
        resp = await client.post(
            "/api/v1/jobs/processar-regua?simular_horario=2026-03-25T10:00:00Z",
            headers=AUTH,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "faturas_processadas" in data
        assert "cobrancas_criadas" in data
        assert "bloqueadas_compliance" in data

    @pytest.mark.asyncio
    async def test_sem_faturas_vencidas_retorna_zeros(self, client):
        await _seed_regua(client)
        resp = await client.post(
            "/api/v1/jobs/processar-regua?simular_horario=2026-03-25T10:00:00Z",
            headers=AUTH,
        )
        data = resp.json()
        assert data["faturas_processadas"] == 0
        assert data["cobrancas_criadas"] == 0

    @pytest.mark.asyncio
    async def test_processa_fatura_vencida(self, client):
        await _seed_regua(client)
        cli = await _create_cliente(client)
        await _create_fatura_vencida(client, cli["id"])

        resp = await client.post(
            "/api/v1/jobs/processar-regua?simular_horario=2026-03-25T10:00:00Z",
            headers=AUTH,
        )
        data = resp.json()
        assert data["faturas_processadas"] == 1
        assert data["cobrancas_criadas"] == 1

    @pytest.mark.asyncio
    async def test_nao_repete_mesmo_passo(self, client):
        """Rodar régua 2x seguidas não duplica cobrança do mesmo passo."""
        await _seed_regua(client)
        cli = await _create_cliente(client)
        await _create_fatura_vencida(client, cli["id"])

        await client.post(
            "/api/v1/jobs/processar-regua?simular_horario=2026-03-25T10:00:00Z",
            headers=AUTH,
        )
        resp = await client.post(
            "/api/v1/jobs/processar-regua?simular_horario=2026-03-25T11:00:00Z",
            headers=AUTH,
        )
        data = resp.json()
        # Segunda execução: passo já executado + compliance 1/dia
        assert data["cobrancas_criadas"] == 0

    @pytest.mark.asyncio
    async def test_fatura_paga_nao_recebe_cobranca(self, client):
        await _seed_regua(client)
        cli = await _create_cliente(client)
        fat = await _create_fatura_vencida(client, cli["id"])

        # Pagar a fatura
        await client.patch(
            f"/api/v1/faturas/{fat['id']}",
            json={"status": "pago"},
            headers=AUTH,
        )

        resp = await client.post(
            "/api/v1/jobs/processar-regua?simular_horario=2026-03-25T10:00:00Z",
            headers=AUTH,
        )
        data = resp.json()
        assert data["cobrancas_criadas"] == 0

    @pytest.mark.asyncio
    async def test_requer_auth(self, client):
        resp = await client.post("/api/v1/jobs/processar-regua")
        assert resp.status_code == 401


# --- Seed régua ---


class TestSeedRegua:
    @pytest.mark.asyncio
    async def test_seed_cria_regua_com_5_passos(self, client):
        data = await _seed_regua(client)
        assert data["regua"] == "Régua Padrão UÚBA"
        assert data["passos"] == 5

    @pytest.mark.asyncio
    async def test_seed_idempotente(self, client):
        await _seed_regua(client)
        data = await _seed_regua(client)
        assert data["passos"] == 5
