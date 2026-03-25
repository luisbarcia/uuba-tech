"""Testes LGPD: política de retenção de dados.

Art. 15/16 — Término do tratamento e eliminação de dados.
"""

import pytest

from app.config import settings

AUTH = {"X-API-Key": settings.api_key}


async def _create_cliente(client, **overrides):
    defaults = dict(nome="Teste Retenção", documento="52998224725")
    defaults.update(overrides)
    resp = await client.post("/api/v1/clientes", json=defaults, headers=AUTH)
    assert resp.status_code == 201
    return resp.json()


async def _create_fatura(client, cliente_id, **overrides):
    defaults = dict(
        cliente_id=cliente_id,
        valor=100000,
        vencimento="2020-01-01T00:00:00Z",
    )
    defaults.update(overrides)
    resp = await client.post("/api/v1/faturas", json=defaults, headers=AUTH)
    assert resp.status_code == 201
    return resp.json()


class TestEndpointCleanup:
    @pytest.mark.asyncio
    async def test_cleanup_retorna_relatorio(self, client):
        """POST /admin/cleanup retorna contadores."""
        resp = await client.post("/api/v1/admin/cleanup", headers=AUTH)
        assert resp.status_code == 200
        data = resp.json()
        assert "mensagens_limpas" in data
        assert "clientes_anonimizados" in data

    @pytest.mark.asyncio
    async def test_cleanup_sem_dados_antigos_retorna_zeros(self, client):
        """Quando não há dados antigos, contadores são zero."""
        resp = await client.post("/api/v1/admin/cleanup", headers=AUTH)
        data = resp.json()
        assert data["mensagens_limpas"] == 0
        assert data["clientes_anonimizados"] == 0

    @pytest.mark.asyncio
    async def test_cleanup_requer_autenticacao(self, client):
        resp = await client.post("/api/v1/admin/cleanup")
        assert resp.status_code == 401
