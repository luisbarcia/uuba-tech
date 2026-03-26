"""Testes do endpoint POST /api/v1/admin/reset (alias para DELETE)."""

import pytest

from tests.conftest import AUTH, create_test_cliente


class TestAdminResetPost:
    @pytest.mark.asyncio
    async def test_reset_post_works(self, client):
        await create_test_cliente(client, documento="11111111000111")

        resp = await client.post(
            "/api/v1/admin/reset?confirm=delete-all-data",
            headers=AUTH,
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "ok"
        assert "deleted" in body
        assert body["deleted"]["clientes"] >= 1

    @pytest.mark.asyncio
    async def test_reset_post_requires_confirmation(self, client):
        resp = await client.post(
            "/api/v1/admin/reset?confirm=wrong",
            headers=AUTH,
        )
        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_reset_post_requires_auth(self, client):
        resp = await client.post("/api/v1/admin/reset?confirm=delete-all-data")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_reset_delete_still_works(self, client):
        """DELETE original continua funcionando."""
        resp = await client.delete(
            "/api/v1/admin/reset?confirm=delete-all-data",
            headers=AUTH,
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"
