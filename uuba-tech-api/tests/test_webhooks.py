"""Testes dos endpoints CRUD de webhooks."""

import pytest

from tests.conftest import AUTH


class TestWebhooksList:
    @pytest.mark.asyncio
    async def test_list_empty(self, client):
        resp = await client.get("/api/v1/webhooks", headers=AUTH)
        assert resp.status_code == 200
        assert resp.json() == []

    @pytest.mark.asyncio
    async def test_list_requires_auth(self, client):
        resp = await client.get("/api/v1/webhooks")
        assert resp.status_code == 401


class TestWebhooksCreate:
    @pytest.mark.asyncio
    async def test_create_webhook(self, client):
        resp = await client.post(
            "/api/v1/webhooks",
            json={"url": "https://example.com/hook", "events": ["invoice.paid"]},
            headers=AUTH,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["url"] == "https://example.com/hook"
        assert data["events"] == ["invoice.paid"]
        assert data["active"] is True
        assert "id" in data

    @pytest.mark.asyncio
    async def test_create_requires_auth(self, client):
        resp = await client.post(
            "/api/v1/webhooks",
            json={"url": "https://example.com/hook", "events": ["invoice.paid"]},
        )
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_create_missing_url(self, client):
        resp = await client.post(
            "/api/v1/webhooks",
            json={"events": ["invoice.paid"]},
            headers=AUTH,
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_create_missing_events(self, client):
        resp = await client.post(
            "/api/v1/webhooks",
            json={"url": "https://example.com/hook"},
            headers=AUTH,
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_create_empty_events(self, client):
        resp = await client.post(
            "/api/v1/webhooks",
            json={"url": "https://example.com/hook", "events": []},
            headers=AUTH,
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_create_and_list(self, client):
        await client.post(
            "/api/v1/webhooks",
            json={"url": "https://example.com/hook", "events": ["*"]},
            headers=AUTH,
        )
        resp = await client.get("/api/v1/webhooks", headers=AUTH)
        assert resp.status_code == 200
        assert len(resp.json()) >= 1


class TestWebhooksTest:
    @pytest.mark.asyncio
    async def test_test_webhook(self, client):
        create_resp = await client.post(
            "/api/v1/webhooks",
            json={"url": "https://example.com/hook", "events": ["*"]},
            headers=AUTH,
        )
        webhook_id = create_resp.json()["id"]

        resp = await client.post(f"/api/v1/webhooks/{webhook_id}/test", headers=AUTH)
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

    @pytest.mark.asyncio
    async def test_test_nonexistent(self, client):
        resp = await client.post("/api/v1/webhooks/whk_nonexistent/test", headers=AUTH)
        assert resp.status_code == 404


class TestWebhooksDelete:
    @pytest.mark.asyncio
    async def test_delete_webhook(self, client):
        create_resp = await client.post(
            "/api/v1/webhooks",
            json={"url": "https://example.com/hook", "events": ["*"]},
            headers=AUTH,
        )
        webhook_id = create_resp.json()["id"]

        resp = await client.delete(f"/api/v1/webhooks/{webhook_id}", headers=AUTH)
        assert resp.status_code == 204

        # Verify deleted
        list_resp = await client.get("/api/v1/webhooks", headers=AUTH)
        ids = [w["id"] for w in list_resp.json()]
        assert webhook_id not in ids

    @pytest.mark.asyncio
    async def test_delete_nonexistent(self, client):
        resp = await client.delete("/api/v1/webhooks/whk_nonexistent", headers=AUTH)
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_requires_auth(self, client):
        resp = await client.delete("/api/v1/webhooks/whk_xxx")
        assert resp.status_code == 401
