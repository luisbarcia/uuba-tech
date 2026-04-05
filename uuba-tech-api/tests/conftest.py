import os

os.environ["TESTING"] = "1"

import pytest
from datetime import datetime, timezone, timedelta
from httpx import AsyncClient, ASGITransport
from sqlalchemy import event
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool

from app.models.base import Base
from app.models.audit_log import AuditLog  # noqa: F401 — registra tabela no metadata
from app.models.regua import Regua, ReguaPasso  # noqa: F401
from app.models.tenant import Tenant  # noqa: F401
from app.models.webhook import Webhook  # noqa: F401
from app.main import app
from app.database import (
    get_db,
    get_fatura_repository,
    get_cobranca_repository,
    get_cliente_repository,
)
from app.infrastructure.repositories.sqlalchemy_fatura_repo import SqlAlchemyFaturaRepository
from app.infrastructure.repositories.sqlalchemy_cobranca_repo import SqlAlchemyCobrancaRepository
from app.infrastructure.repositories.sqlalchemy_cliente_repo import SqlAlchemyClienteRepository
from app.auth.api_key import clear_tenant_cache, verify_api_key
from app.config import settings
from fastapi import Request

TEST_TENANT_ID = "ten_test"
API_KEY = settings.api_key
AUTH = {"X-API-Key": API_KEY}


@pytest.fixture
async def engine():
    _engine = create_async_engine(
        "sqlite+aiosqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(_engine.sync_engine, "connect")
    def enable_fk(dbapi_conn, _):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Criar tenant de teste
    factory = async_sessionmaker(_engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        session.add(
            Tenant(
                id=TEST_TENANT_ID,
                nome="Tenant Teste",
                slug="tenant-teste",
                documento="00000000000100",
                api_key=API_KEY,
                ativo=True,
                plan="starter",
            )
        )
        await session.commit()

    yield _engine

    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await _engine.dispose()


@pytest.fixture
async def client(engine):
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db():
        async with factory() as session:
            yield session

    async def override_fatura_repo():
        async with factory() as session:
            yield SqlAlchemyFaturaRepository(session, TEST_TENANT_ID)

    async def override_cobranca_repo():
        async with factory() as session:
            yield SqlAlchemyCobrancaRepository(session, TEST_TENANT_ID)

    async def override_cliente_repo():
        async with factory() as session:
            yield SqlAlchemyClienteRepository(session, TEST_TENANT_ID)

    async def override_verify_api_key(request: Request):
        """Override padrao: valida key contra API_KEY e da permissoes admin."""
        from app.exceptions import APIError

        api_key = request.headers.get("X-API-Key", "")
        if not api_key or api_key != API_KEY:
            raise APIError(
                401, "auth-invalida", "Autenticacao invalida", "API key ausente ou invalida"
            )
        request.state.tenant_id = TEST_TENANT_ID
        request.state.permissions = ["tenants:write", "tenants:read", "admin:write", "admin:read"]
        request.state.key_id = "key_test"
        return api_key

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_fatura_repository] = override_fatura_repo
    app.dependency_overrides[get_cobranca_repository] = override_cobranca_repo
    app.dependency_overrides[get_cliente_repository] = override_cliente_repo
    app.dependency_overrides[verify_api_key] = override_verify_api_key

    clear_tenant_cache()

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac
    app.dependency_overrides.clear()
    clear_tenant_cache()


# --- Helpers ---


async def create_test_cliente(c: AsyncClient, **overrides) -> dict:
    data = {
        "nome": "Padaria Bom Pao",
        "documento": "12345678000190",
        "email": "contato@padaria.com",
        "telefone": "5511999001234",
        **overrides,
    }
    resp = await c.post("/api/v1/clientes", json=data, headers=AUTH)
    assert resp.status_code == 201, resp.text
    return resp.json()


async def create_test_fatura(c: AsyncClient, cliente_id: str, **overrides) -> dict:
    data = {
        "cliente_id": cliente_id,
        "valor": 250000,
        "vencimento": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
        "descricao": "NF 1234 - Servicos marco",
        **overrides,
    }
    resp = await c.post("/api/v1/faturas", json=data, headers=AUTH)
    assert resp.status_code == 201, resp.text
    return resp.json()


async def create_test_cobranca(
    c: AsyncClient, fatura_id: str, cliente_id: str, **overrides
) -> dict:
    data = {
        "fatura_id": fatura_id,
        "cliente_id": cliente_id,
        "tipo": "lembrete",
        "canal": "whatsapp",
        **overrides,
    }
    resp = await c.post("/api/v1/cobrancas", json=data, headers=AUTH)
    assert resp.status_code == 201, resp.text
    return resp.json()


# --- v0/faturas fixture (receivables:write) ---

@pytest.fixture
async def v0_client(engine):
    """Client HTTP com receivables:write nas permissions (para v0/faturas)."""
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db():
        async with factory() as session:
            yield session

    async def override_fatura_repo():
        async with factory() as session:
            yield SqlAlchemyFaturaRepository(session, TEST_TENANT_ID)

    async def override_cobranca_repo():
        async with factory() as session:
            yield SqlAlchemyCobrancaRepository(session, TEST_TENANT_ID)

    async def override_cliente_repo():
        async with factory() as session:
            yield SqlAlchemyClienteRepository(session, TEST_TENANT_ID)

    async def override_verify_api_key(request: Request):
        from app.exceptions import APIError

        api_key = request.headers.get("X-API-Key", "")
        if not api_key or api_key != API_KEY:
            raise APIError(
                401, "auth-invalida", "Autenticacao invalida", "API key ausente ou invalida"
            )
        request.state.tenant_id = TEST_TENANT_ID
        request.state.permissions = ["receivables:write"]
        request.state.key_id = "key_test"
        return api_key

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_fatura_repository] = override_fatura_repo
    app.dependency_overrides[get_cobranca_repository] = override_cobranca_repo
    app.dependency_overrides[get_cliente_repository] = override_cliente_repo
    app.dependency_overrides[verify_api_key] = override_verify_api_key

    clear_tenant_cache()

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac
    app.dependency_overrides.clear()
    clear_tenant_cache()
