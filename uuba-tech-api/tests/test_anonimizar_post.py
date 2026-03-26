"""Testes do endpoint POST /api/v1/clientes/{id}/anonimizar (LGPD Art. 18).

Diferente do DELETE que retorna 204, o POST retorna o cliente anonimizado.
"""

import pytest

from tests.conftest import AUTH, create_test_cliente, create_test_fatura, create_test_cobranca


class TestAnonimizarPost:
    @pytest.mark.asyncio
    async def test_anonimizar_returns_200_with_data(self, client):
        cli = await create_test_cliente(
            client,
            nome="Maria Silva",
            documento="52998224725",
            email="maria@test.com",
            telefone="5511999001234",
        )

        resp = await client.post(
            f"/api/v1/clientes/{cli['id']}/anonimizar",
            headers=AUTH,
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["id"] == cli["id"]
        assert body["object"] == "cliente"
        # Dados devem estar anonimizados
        assert body["nome"] == "REMOVIDO"
        assert body["documento"] != "52998224725"
        assert body["email"] is None
        assert body["telefone"] is None

    @pytest.mark.asyncio
    async def test_anonimizar_not_found(self, client):
        resp = await client.post(
            "/api/v1/clientes/cli_naoexiste00/anonimizar",
            headers=AUTH,
        )
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_anonimizar_requires_auth(self, client):
        resp = await client.post("/api/v1/clientes/cli_qualquer/anonimizar")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_anonimizar_preserva_faturas(self, client):
        """Faturas devem continuar existindo apos anonimizacao."""
        cli = await create_test_cliente(client)
        fat = await create_test_fatura(client, cli["id"])

        await client.post(
            f"/api/v1/clientes/{cli['id']}/anonimizar",
            headers=AUTH,
        )

        resp = await client.get(f"/api/v1/faturas/{fat['id']}", headers=AUTH)
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_anonimizar_limpa_mensagens(self, client):
        """Mensagens de cobranca devem ser removidas."""
        cli = await create_test_cliente(client)
        fat = await create_test_fatura(client, cli["id"])
        await create_test_cobranca(
            client,
            fat["id"],
            cli["id"],
            mensagem="Ola Maria, lembrete de pagamento",
        )

        await client.post(
            f"/api/v1/clientes/{cli['id']}/anonimizar",
            headers=AUTH,
        )

        resp = await client.get(f"/api/v1/cobrancas/{fat['id']}/historico", headers=AUTH)
        assert resp.status_code == 200
        for c in resp.json()["data"]:
            assert c["mensagem"] is None

    @pytest.mark.asyncio
    async def test_anonimizar_idempotente_404(self, client):
        """Anonimizar cliente ja anonimizado retorna 404."""
        cli = await create_test_cliente(client)
        resp1 = await client.post(
            f"/api/v1/clientes/{cli['id']}/anonimizar",
            headers=AUTH,
        )
        assert resp1.status_code == 200

        resp2 = await client.post(
            f"/api/v1/clientes/{cli['id']}/anonimizar",
            headers=AUTH,
        )
        assert resp2.status_code == 404
