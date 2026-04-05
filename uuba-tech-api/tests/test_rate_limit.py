"""Testes do RateLimitMiddleware com middleware ativo.

Desabilita TESTING env var para ativar o rate limiter e verifica 429
após exceder o threshold. Usa /docs (não requer auth, não é exempt).

Issue: #95
"""

import os
from unittest.mock import patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.middleware.rate_limit import RateLimitMiddleware


@pytest.fixture
async def rate_limited_client():
    """Client com rate limiter ativo e limite baixo (3 req/60s)."""
    original_limit = None

    for middleware in app.user_middleware:
        if middleware.cls is RateLimitMiddleware:
            original_limit = middleware.kwargs.get("rate_limit", 100)
            middleware.kwargs["rate_limit"] = 3
            break

    app.middleware_stack = app.build_middleware_stack()

    env = {k: v for k, v in os.environ.items() if k != "TESTING"}
    with patch.dict(os.environ, env, clear=True):
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as ac:
            yield ac

    for middleware in app.user_middleware:
        if middleware.cls is RateLimitMiddleware:
            middleware.kwargs["rate_limit"] = original_limit or 100
            break
    app.middleware_stack = app.build_middleware_stack()


class TestRateLimiterActive:
    @pytest.mark.asyncio
    async def test_returns_429_after_threshold(self, rate_limited_client):
        """Após 3 requests, o 4o retorna 429."""
        c = rate_limited_client

        for i in range(3):
            resp = await c.get("/docs")
            assert resp.status_code == 200, f"Request {i + 1}: esperava 200, got {resp.status_code}"

        resp = await c.get("/docs")
        assert resp.status_code == 429
        body = resp.json()
        assert body["status"] == 429

    @pytest.mark.asyncio
    async def test_429_body_has_problem_details(self, rate_limited_client):
        """Response 429 segue RFC 9457 com type, title, detail."""
        c = rate_limited_client

        for _ in range(3):
            await c.get("/docs")

        resp = await c.get("/docs")
        assert resp.status_code == 429
        body = resp.json()
        assert "type" in body
        assert "title" in body
        assert "detail" in body

    @pytest.mark.asyncio
    async def test_exempt_path_not_counted(self, rate_limited_client):
        """/api/v1/privacidade (exempt) não conta para rate limit."""
        c = rate_limited_client

        # Privacidade é exempt e não requer DB
        for _ in range(10):
            resp = await c.get("/api/v1/privacidade")
            # Pode dar 404/405 mas nunca 429
            assert resp.status_code != 429

    @pytest.mark.asyncio
    async def test_different_keys_have_separate_counters(self, rate_limited_client):
        """Keys diferentes têm contadores independentes."""
        c = rate_limited_client

        for _ in range(3):
            await c.get("/docs", headers={"X-API-Key": "key-a"})

        resp = await c.get("/docs", headers={"X-API-Key": "key-a"})
        assert resp.status_code == 429

        resp = await c.get("/docs", headers={"X-API-Key": "key-b"})
        assert resp.status_code == 200
