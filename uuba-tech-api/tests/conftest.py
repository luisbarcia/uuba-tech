import pytest
from datetime import datetime, timezone, timedelta
from httpx import AsyncClient, ASGITransport
from sqlalchemy import event
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool

from app.models.base import Base
from app.main import app
from app.database import get_db
from app.config import settings

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

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac
    app.dependency_overrides.clear()


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
