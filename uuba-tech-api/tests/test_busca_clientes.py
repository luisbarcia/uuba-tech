"""Testes do endpoint de busca de clientes (GET /api/v1/clientes/busca)."""

import pytest

from tests.conftest import AUTH, create_test_cliente


class TestBuscaClientes:
    @pytest.mark.asyncio
    async def test_busca_por_nome(self, client):
        await create_test_cliente(client, nome="Padaria Estrela", documento="11111111000111")
        await create_test_cliente(client, nome="Loja Solar", documento="22222222000122")

        resp = await client.get("/api/v1/clientes/busca?q=Padaria", headers=AUTH)
        assert resp.status_code == 200
        body = resp.json()
        assert body["object"] == "list"
        assert body["pagination"]["total"] == 1
        assert body["data"][0]["nome"] == "Padaria Estrela"

    @pytest.mark.asyncio
    async def test_busca_por_documento(self, client):
        await create_test_cliente(client, nome="Empresa A", documento="33333333000133")
        await create_test_cliente(client, nome="Empresa B", documento="44444444000144")

        resp = await client.get("/api/v1/clientes/busca?q=33333333", headers=AUTH)
        assert resp.status_code == 200
        body = resp.json()
        assert body["pagination"]["total"] == 1
        assert body["data"][0]["nome"] == "Empresa A"

    @pytest.mark.asyncio
    async def test_busca_por_telefone(self, client):
        await create_test_cliente(
            client, nome="Com Tel", documento="55555555000155", telefone="5511888887777"
        )
        await create_test_cliente(
            client, nome="Sem Tel", documento="66666666000166", telefone="5521999990000"
        )

        resp = await client.get("/api/v1/clientes/busca?q=5511888", headers=AUTH)
        assert resp.status_code == 200
        body = resp.json()
        assert body["pagination"]["total"] == 1
        assert body["data"][0]["nome"] == "Com Tel"

    @pytest.mark.asyncio
    async def test_busca_sem_resultados(self, client):
        await create_test_cliente(client, documento="77777777000177")

        resp = await client.get("/api/v1/clientes/busca?q=inexistente", headers=AUTH)
        assert resp.status_code == 200
        body = resp.json()
        assert body["pagination"]["total"] == 0
        assert body["data"] == []

    @pytest.mark.asyncio
    async def test_busca_case_insensitive(self, client):
        await create_test_cliente(client, nome="PADARIA GRANDE", documento="88888888000188")

        resp = await client.get("/api/v1/clientes/busca?q=padaria", headers=AUTH)
        assert resp.status_code == 200
        assert resp.json()["pagination"]["total"] == 1

    @pytest.mark.asyncio
    async def test_busca_paginacao(self, client):
        for i in range(5):
            await create_test_cliente(client, nome=f"Busca Pag {i}", documento=f"9999999{i:07d}")

        resp = await client.get("/api/v1/clientes/busca?q=Busca+Pag&limit=2&offset=0", headers=AUTH)
        body = resp.json()
        assert len(body["data"]) == 2
        assert body["pagination"]["total"] == 5
        assert body["pagination"]["has_more"] is True

    @pytest.mark.asyncio
    async def test_busca_sem_q_returns_422(self, client):
        resp = await client.get("/api/v1/clientes/busca", headers=AUTH)
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_busca_requires_auth(self, client):
        resp = await client.get("/api/v1/clientes/busca?q=teste")
        assert resp.status_code == 401
