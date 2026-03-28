"""Testes dos endpoints GET /api/v1/logs e GET /api/v1/logs/search."""

import pytest

from tests.conftest import AUTH


class TestLogs:
    @pytest.mark.asyncio
    async def test_list_logs_returns_200(self, client):
        resp = await client.get("/api/v1/logs", headers=AUTH)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    @pytest.mark.asyncio
    async def test_list_logs_requires_auth(self, client):
        resp = await client.get("/api/v1/logs")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_list_logs_respects_limit(self, client):
        resp = await client.get("/api/v1/logs?limit=5", headers=AUTH)
        assert resp.status_code == 200
        assert len(resp.json()) <= 5

    @pytest.mark.asyncio
    async def test_list_logs_empty_db(self, client):
        resp = await client.get("/api/v1/logs", headers=AUTH)
        assert resp.status_code == 200
        assert resp.json() == []


class TestLogsSearch:
    @pytest.mark.asyncio
    async def test_search_requires_query(self, client):
        resp = await client.get("/api/v1/logs/search", headers=AUTH)
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_search_returns_200(self, client):
        resp = await client.get("/api/v1/logs/search?q=test", headers=AUTH)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    @pytest.mark.asyncio
    async def test_search_requires_auth(self, client):
        resp = await client.get("/api/v1/logs/search?q=test")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_search_with_like_wildcards(self, client):
        """Wildcards LIKE nao devem causar erro."""
        resp = await client.get("/api/v1/logs/search?q=%25", headers=AUTH)
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_search_with_since_until(self, client):
        resp = await client.get(
            "/api/v1/logs/search?q=test&since=2020-01-01T00:00:00Z&until=2030-01-01T00:00:00Z",
            headers=AUTH,
        )
        assert resp.status_code == 200
