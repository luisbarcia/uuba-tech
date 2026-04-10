"""Tests for auth cache TTL — entries expire after CACHE_TTL_SECONDS."""

import os

os.environ["TESTING"] = "1"

import time

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.auth import api_key as auth_module
from app.auth.api_key import (
    CACHE_TTL_SECONDS,
    _get_cached,
    _set_cached,
    clear_tenant_cache,
)
from app.config import settings
from app.database import get_db
from app.main import app
from app.models.audit_log import AuditLog  # noqa: F401
from app.models.base import Base
from app.models.regua import Regua, ReguaPasso  # noqa: F401
from app.models.tenant import Tenant

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

    factory = async_sessionmaker(_engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        session.add(
            Tenant(
                id=TEST_TENANT_ID,
                nome="Tenant Teste",
                slug="tenant-teste",
                documento="00000000000100",
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

    app.dependency_overrides[get_db] = override_get_db
    clear_tenant_cache()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


class TestCacheHelpers:
    """Unit tests for _get_cached / _set_cached."""

    def test_ttl_constant_is_300(self):
        assert CACHE_TTL_SECONDS == 300

    def test_set_and_get_returns_value(self):
        cache: dict = {}
        _set_cached(cache, "k1", "v1")
        assert _get_cached(cache, "k1") == "v1"

    def test_expired_entry_returns_none(self):
        cache: dict = {}
        _set_cached(cache, "k1", "v1")
        cache["k1"] = ("v1", time.monotonic() - CACHE_TTL_SECONDS - 1)
        assert _get_cached(cache, "k1") is None

    def test_expired_entry_is_deleted(self):
        cache: dict = {}
        _set_cached(cache, "k1", "v1")
        cache["k1"] = ("v1", time.monotonic() - CACHE_TTL_SECONDS - 1)
        _get_cached(cache, "k1")
        assert "k1" not in cache

    def test_missing_key_returns_none(self):
        cache: dict = {}
        assert _get_cached(cache, "nope") is None

    def test_fresh_entry_returns_value(self):
        cache: dict = {}
        _set_cached(cache, "k1", "v1")
        assert _get_cached(cache, "k1") == "v1"


class TestClearCache:
    """clear_tenant_cache empties unkey cache."""

    def test_clears_unkey_cache(self):
        auth_module._unkey_cache["x"] = ({"d": 1}, time.monotonic())
        clear_tenant_cache()
        assert len(auth_module._unkey_cache) == 0
