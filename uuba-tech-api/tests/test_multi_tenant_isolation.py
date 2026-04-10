"""Testes de isolamento multi-tenant.

CRÍTICO: Garante que dados de um tenant NUNCA vazam para outro.
Cria 2 tenants independentes e verifica isolamento em todas as camadas.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from app.auth.api_key import clear_tenant_cache, verify_api_key
from app.database import (
    get_cliente_repository,
    get_cobranca_repository,
    get_db,
    get_fatura_repository,
)
from app.infrastructure.repositories.sqlalchemy_cliente_repo import (
    SqlAlchemyClienteRepository,
)
from app.infrastructure.repositories.sqlalchemy_cobranca_repo import (
    SqlAlchemyCobrancaRepository,
)
from app.infrastructure.repositories.sqlalchemy_fatura_repo import (
    SqlAlchemyFaturaRepository,
)
from app.main import app
from app.models.tenant import Tenant

TENANT_A_KEY = "key-tenant-a-isolation-test"
TENANT_B_KEY = "key-tenant-b-isolation-test"
AUTH_A = {"X-API-Key": TENANT_A_KEY}
AUTH_B = {"X-API-Key": TENANT_B_KEY}


@pytest.fixture
async def two_tenant_client(engine):
    """Fixture que cria 2 tenants isolados e retorna um client HTTP."""
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # Criar tenants A e B
    async with factory() as session:
        session.add(
            Tenant(
                id="ten_a",
                nome="Empresa A",
                slug="empresa-a",
                documento="11111111000100",
                ativo=True,
            )
        )
        session.add(
            Tenant(
                id="ten_b",
                nome="Empresa B",
                slug="empresa-b",
                documento="22222222000100",
                ativo=True,
            )
        )
        await session.commit()

    # Override DI para usar a mesma engine mas respeitando tenant do request
    async def override_get_db():
        async with factory() as session:
            yield session

    # Estes overrides NÃO hardcodam tenant — usam o do request.state
    # Para isso, NÃO sobrescrevemos os repos; deixamos o DI padrão funcionar
    # Mas precisamos que get_db use nossa engine de teste
    app.dependency_overrides[get_db] = override_get_db

    # Auth override: mapeia key → tenant_id (sem depender de Tenant.api_key no DB)
    from fastapi import Request as _Req
    from app.exceptions import APIError as _Err

    KEY_TO_TENANT = {TENANT_A_KEY: "ten_a", TENANT_B_KEY: "ten_b"}

    async def override_verify_api_key(request: _Req):
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            key = auth_header[7:]
        else:
            key = request.headers.get("X-API-Key", "")
        tenant_id = KEY_TO_TENANT.get(key)
        if not tenant_id:
            raise _Err(401, "auth-invalida", "Autenticacao invalida", "API key ausente ou invalida")
        request.state.tenant_id = tenant_id
        request.state.permissions = ["*"]
        request.state.key_id = "key_test"
        request.state.environment = "test"
        return key

    app.dependency_overrides[verify_api_key] = override_verify_api_key

    # Precisamos sobrescrever os repos para usar a engine de teste
    # mas com o tenant correto do request
    from fastapi import Request

    async def override_fatura_repo(request: Request):
        tenant_id = request.state.tenant_id
        async with factory() as session:
            yield SqlAlchemyFaturaRepository(session, tenant_id)

    async def override_cobranca_repo(request: Request):
        tenant_id = request.state.tenant_id
        async with factory() as session:
            yield SqlAlchemyCobrancaRepository(session, tenant_id)

    async def override_cliente_repo(request: Request):
        tenant_id = request.state.tenant_id
        async with factory() as session:
            yield SqlAlchemyClienteRepository(session, tenant_id)

    app.dependency_overrides[get_fatura_repository] = override_fatura_repo
    app.dependency_overrides[get_cobranca_repository] = override_cobranca_repo
    app.dependency_overrides[get_cliente_repository] = override_cliente_repo

    clear_tenant_cache()

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
    clear_tenant_cache()


# --- Isolamento de Clientes ---


class TestIsolamentoClientes:
    @pytest.mark.asyncio
    async def test_tenant_a_nao_ve_clientes_de_b(self, two_tenant_client):
        c = two_tenant_client

        # Tenant A cria cliente
        resp_a = await c.post(
            "/api/v1/clientes",
            json={"nome": "Cliente de A", "documento": "52998224725"},
            headers=AUTH_A,
        )
        assert resp_a.status_code == 201
        cli_a_id = resp_a.json()["id"]

        # Tenant B cria cliente com documento diferente
        resp_b = await c.post(
            "/api/v1/clientes",
            json={"nome": "Cliente de B", "documento": "11444777000161"},
            headers=AUTH_B,
        )
        assert resp_b.status_code == 201

        # Tenant A lista: só vê seu cliente
        resp_list_a = await c.get("/api/v1/clientes", headers=AUTH_A)
        nomes_a = [cli["nome"] for cli in resp_list_a.json()["data"]]
        assert "Cliente de A" in nomes_a
        assert "Cliente de B" not in nomes_a

        # Tenant B lista: só vê seu cliente
        resp_list_b = await c.get("/api/v1/clientes", headers=AUTH_B)
        nomes_b = [cli["nome"] for cli in resp_list_b.json()["data"]]
        assert "Cliente de B" in nomes_b
        assert "Cliente de A" not in nomes_b

        # Tenant B tenta acessar cliente de A por ID: 404
        resp_cross = await c.get(f"/api/v1/clientes/{cli_a_id}", headers=AUTH_B)
        assert resp_cross.status_code == 404

    @pytest.mark.asyncio
    async def test_mesmo_documento_em_tenants_diferentes(self, two_tenant_client):
        """Mesmo CPF pode existir em tenants diferentes (devedor deve para 2 credores)."""
        c = two_tenant_client
        doc = "52998224725"

        resp_a = await c.post(
            "/api/v1/clientes",
            json={"nome": "Maria em A", "documento": doc},
            headers=AUTH_A,
        )
        assert resp_a.status_code == 201

        resp_b = await c.post(
            "/api/v1/clientes",
            json={"nome": "Maria em B", "documento": doc},
            headers=AUTH_B,
        )
        assert resp_b.status_code == 201  # NÃO deve dar 409

        assert resp_a.json()["id"] != resp_b.json()["id"]


# --- Isolamento de Faturas ---


class TestIsolamentoFaturas:
    @pytest.mark.asyncio
    async def test_tenant_a_nao_ve_faturas_de_b(self, two_tenant_client):
        c = two_tenant_client

        # Cada tenant cria seu cliente e fatura
        cli_a = await c.post(
            "/api/v1/clientes",
            json={"nome": "Cli A", "documento": "52998224725"},
            headers=AUTH_A,
        )
        fat_a = await c.post(
            "/api/v1/faturas",
            json={
                "cliente_id": cli_a.json()["id"],
                "valor": 100000,
                "vencimento": "2026-04-01T00:00:00Z",
            },
            headers=AUTH_A,
        )
        assert fat_a.status_code == 201
        fat_a_id = fat_a.json()["id"]

        cli_b = await c.post(
            "/api/v1/clientes",
            json={"nome": "Cli B", "documento": "11444777000161"},
            headers=AUTH_B,
        )
        await c.post(
            "/api/v1/faturas",
            json={
                "cliente_id": cli_b.json()["id"],
                "valor": 200000,
                "vencimento": "2026-04-01T00:00:00Z",
            },
            headers=AUTH_B,
        )

        # Tenant A lista faturas: só vê a sua
        resp = await c.get("/api/v1/faturas", headers=AUTH_A)
        ids_a = [f["id"] for f in resp.json()["data"]]
        assert len(ids_a) == 1

        # Tenant B tenta acessar fatura de A: 404
        resp_cross = await c.get(f"/api/v1/faturas/{fat_a_id}", headers=AUTH_B)
        assert resp_cross.status_code == 404


# --- Isolamento de Cobranças ---


class TestIsolamentoCobrancas:
    @pytest.mark.asyncio
    async def test_tenant_a_nao_ve_cobrancas_de_b(self, two_tenant_client):
        c = two_tenant_client

        # Tenant A cria cliente + fatura + cobrança
        cli_a = await c.post(
            "/api/v1/clientes",
            json={"nome": "Devedor A", "documento": "52998224725"},
            headers=AUTH_A,
        )
        fat_a = await c.post(
            "/api/v1/faturas",
            json={
                "cliente_id": cli_a.json()["id"],
                "valor": 100000,
                "vencimento": "2026-04-01T00:00:00Z",
            },
            headers=AUTH_A,
        )
        await c.post(
            "/api/v1/cobrancas",
            json={
                "fatura_id": fat_a.json()["id"],
                "cliente_id": cli_a.json()["id"],
                "tipo": "lembrete",
            },
            headers=AUTH_A,
        )

        # Tenant B lista cobranças: vazio
        resp_b = await c.get("/api/v1/cobrancas", headers=AUTH_B)
        assert resp_b.json()["pagination"]["total"] == 0


# --- Isolamento LGPD (dados pessoais / anonimização) ---


class TestIsolamentoLGPD:
    @pytest.mark.asyncio
    async def test_delete_nao_afeta_outro_tenant(self, two_tenant_client):
        """Anonimizar cliente de A não afeta cliente de B com mesmo documento."""
        c = two_tenant_client
        doc = "52998224725"

        cli_a = await c.post(
            "/api/v1/clientes",
            json={"nome": "Maria A", "documento": doc},
            headers=AUTH_A,
        )
        cli_b = await c.post(
            "/api/v1/clientes",
            json={"nome": "Maria B", "documento": doc},
            headers=AUTH_B,
        )

        # Deletar Maria de A
        resp_del = await c.delete(f"/api/v1/clientes/{cli_a.json()['id']}", headers=AUTH_A)
        assert resp_del.status_code == 204

        # Maria de B continua intacta
        resp_b = await c.get(f"/api/v1/clientes/{cli_b.json()['id']}", headers=AUTH_B)
        assert resp_b.status_code == 200
        assert resp_b.json()["nome"] == "Maria B"

    @pytest.mark.asyncio
    async def test_dados_pessoais_isolados(self, two_tenant_client):
        """Endpoint de dados pessoais não vaza dados entre tenants."""
        c = two_tenant_client

        cli_a = await c.post(
            "/api/v1/clientes",
            json={"nome": "Pessoa A", "documento": "52998224725"},
            headers=AUTH_A,
        )

        # Tenant B tenta acessar dados pessoais de cliente de A: 404
        resp = await c.get(
            f"/api/v1/clientes/{cli_a.json()['id']}/dados-pessoais",
            headers=AUTH_B,
        )
        assert resp.status_code == 404
