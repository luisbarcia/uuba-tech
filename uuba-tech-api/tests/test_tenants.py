"""Testes do CRUD de tenants (POST, GET, PATCH)."""

import pytest

from tests.conftest import AUTH


# --- POST /api/v1/tenants ---


class TestCreateTenant:
    @pytest.mark.asyncio
    async def test_create_tenant_returns_201(self, client):
        resp = await client.post(
            "/api/v1/tenants",
            json={"name": "Recbird"},
            headers=AUTH,
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["id"].startswith("ten_")
        assert body["object"] == "tenant"
        assert body["name"] == "Recbird"
        assert body["slug"] == "recbird"
        assert body["active"] is True
        assert body["plan"] == "starter"
        assert "created_at" in body
        assert "updated_at" in body

    @pytest.mark.asyncio
    async def test_create_tenant_auto_slug(self, client):
        resp = await client.post(
            "/api/v1/tenants",
            json={"name": "Recbird Tech Brasil"},
            headers=AUTH,
        )
        assert resp.status_code == 201
        assert resp.json()["slug"] == "recbird-tech-brasil"

    @pytest.mark.asyncio
    async def test_create_tenant_missing_name_returns_422(self, client):
        resp = await client.post(
            "/api/v1/tenants",
            json={},
            headers=AUTH,
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_create_tenant_empty_name_returns_422(self, client):
        resp = await client.post(
            "/api/v1/tenants",
            json={"name": ""},
            headers=AUTH,
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_create_tenant_requires_auth(self, client):
        resp = await client.post(
            "/api/v1/tenants",
            json={"name": "Sem Auth"},
        )
        assert resp.status_code == 401


# --- GET /api/v1/tenants ---


class TestListTenants:
    @pytest.mark.asyncio
    async def test_list_tenants_returns_list(self, client):
        resp = await client.get("/api/v1/tenants", headers=AUTH)
        assert resp.status_code == 200
        body = resp.json()
        assert body["object"] == "list"
        assert "data" in body
        assert "pagination" in body
        # Ao menos o tenant de teste existe
        assert body["pagination"]["total"] >= 1

    @pytest.mark.asyncio
    async def test_list_tenants_pagination(self, client):
        # Criar 3 tenants extras
        for i in range(3):
            await client.post(
                "/api/v1/tenants",
                json={"name": f"Tenant Pag {i}"},
                headers=AUTH,
            )

        resp = await client.get("/api/v1/tenants?limit=2&offset=0", headers=AUTH)
        body = resp.json()
        assert len(body["data"]) == 2
        assert body["pagination"]["has_more"] is True

    @pytest.mark.asyncio
    async def test_list_tenants_requires_auth(self, client):
        resp = await client.get("/api/v1/tenants")
        assert resp.status_code == 401


# --- GET /api/v1/tenants/{tenant_id} ---


class TestGetTenant:
    @pytest.mark.asyncio
    async def test_get_tenant_exists(self, client):
        # Criar tenant
        created = await client.post(
            "/api/v1/tenants",
            json={"name": "Get Teste"},
            headers=AUTH,
        )
        tenant_id = created.json()["id"]

        resp = await client.get(f"/api/v1/tenants/{tenant_id}", headers=AUTH)
        assert resp.status_code == 200
        assert resp.json()["id"] == tenant_id
        assert resp.json()["name"] == "Get Teste"

    @pytest.mark.asyncio
    async def test_get_tenant_not_found(self, client):
        resp = await client.get("/api/v1/tenants/ten_naoexiste00", headers=AUTH)
        assert resp.status_code == 404
        body = resp.json()
        assert body["status"] == 404
        assert "type" in body


# --- PATCH /api/v1/tenants/{tenant_id} ---


class TestUpdateTenant:
    @pytest.mark.asyncio
    async def test_update_tenant_name(self, client):
        created = await client.post(
            "/api/v1/tenants",
            json={"name": "Antes"},
            headers=AUTH,
        )
        tenant_id = created.json()["id"]

        resp = await client.patch(
            f"/api/v1/tenants/{tenant_id}",
            json={"name": "Depois"},
            headers=AUTH,
        )
        assert resp.status_code == 200
        assert resp.json()["name"] == "Depois"
        assert resp.json()["slug"] == "depois"

    @pytest.mark.asyncio
    async def test_update_tenant_active(self, client):
        created = await client.post(
            "/api/v1/tenants",
            json={"name": "Desativar"},
            headers=AUTH,
        )
        tenant_id = created.json()["id"]

        resp = await client.patch(
            f"/api/v1/tenants/{tenant_id}",
            json={"active": False},
            headers=AUTH,
        )
        assert resp.status_code == 200
        assert resp.json()["active"] is False

    @pytest.mark.asyncio
    async def test_update_tenant_plan(self, client):
        created = await client.post(
            "/api/v1/tenants",
            json={"name": "Plano"},
            headers=AUTH,
        )
        tenant_id = created.json()["id"]

        resp = await client.patch(
            f"/api/v1/tenants/{tenant_id}",
            json={"plan": "enterprise"},
            headers=AUTH,
        )
        assert resp.status_code == 200
        assert resp.json()["plan"] == "enterprise"

    @pytest.mark.asyncio
    async def test_update_tenant_invalid_plan_returns_422(self, client):
        created = await client.post(
            "/api/v1/tenants",
            json={"name": "Invalid Plan"},
            headers=AUTH,
        )
        tenant_id = created.json()["id"]

        resp = await client.patch(
            f"/api/v1/tenants/{tenant_id}",
            json={"plan": "ultra"},
            headers=AUTH,
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_update_tenant_not_found(self, client):
        resp = await client.patch(
            "/api/v1/tenants/ten_naoexiste00",
            json={"name": "Teste"},
            headers=AUTH,
        )
        assert resp.status_code == 404
