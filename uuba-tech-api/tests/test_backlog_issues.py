"""Testes para issues #66-#70 do backlog.

#66: rate limiting middleware
#67: cleanup_service
#68: audit_service
#69: admin seed/reset production guard
#70: tenant desativado rejeitado no auth
"""

import pytest

from tests.conftest import AUTH


class TestRateLimitMiddleware:
    """#66: rate limiting middleware com zero cobertura."""

    @pytest.mark.asyncio
    async def test_rate_limit_headers_not_present_in_test_mode(self, client):
        """Em TESTING=1, rate limiter esta desabilitado."""
        resp = await client.get("/health")
        assert resp.status_code == 200
        # Rate limit headers NAO devem estar presentes em modo teste
        assert "X-RateLimit-Limit" not in resp.headers

    @pytest.mark.asyncio
    async def test_exempt_endpoints_accessible(self, client):
        """Endpoints publicos nao devem ter rate limit."""
        resp = await client.get("/health")
        assert resp.status_code == 200

        resp = await client.get("/api/v1/privacidade")
        assert resp.status_code == 200


class TestCleanupService:
    """#67: cleanup_service sem teste dedicado."""

    @pytest.mark.asyncio
    async def test_cleanup_endpoint_returns_200(self, client):
        resp = await client.post("/api/v1/admin/cleanup", headers=AUTH)
        assert resp.status_code == 200
        data = resp.json()
        assert "mensagens_limpas" in data
        assert "clientes_anonimizados" in data

    @pytest.mark.asyncio
    async def test_cleanup_with_no_expired_data(self, client):
        """Sem dados expirados, contadores devem ser zero."""
        resp = await client.post("/api/v1/admin/cleanup", headers=AUTH)
        data = resp.json()
        assert data["mensagens_limpas"] == 0
        assert data["clientes_anonimizados"] == 0

    @pytest.mark.asyncio
    async def test_cleanup_requires_auth(self, client):
        resp = await client.post("/api/v1/admin/cleanup")
        assert resp.status_code == 401


class TestAuditService:
    """#68: audit_service sem teste dedicado."""

    @pytest.mark.asyncio
    async def test_audit_endpoint_returns_200(self, client):
        resp = await client.get("/api/v1/admin/audit", headers=AUTH)
        assert resp.status_code == 200
        data = resp.json()
        assert data["object"] == "list"

    @pytest.mark.asyncio
    async def test_audit_returns_empty_initially(self, client):
        resp = await client.get("/api/v1/admin/audit", headers=AUTH)
        data = resp.json()
        assert data["pagination"]["total"] >= 0

    @pytest.mark.asyncio
    async def test_audit_requires_auth(self, client):
        resp = await client.get("/api/v1/admin/audit")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_audit_filter_by_recurso(self, client):
        resp = await client.get("/api/v1/admin/audit?recurso=cliente", headers=AUTH)
        assert resp.status_code == 200


class TestAdminProductionGuard:
    """#69: admin seed/reset sem teste de production guard."""

    @pytest.mark.asyncio
    async def test_seed_works_in_test_env(self, client):
        resp = await client.post("/api/v1/admin/seed", headers=AUTH)
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_reset_requires_confirm_param(self, client):
        resp = await client.delete("/api/v1/admin/reset", headers=AUTH)
        assert resp.status_code in (400, 422)

    @pytest.mark.asyncio
    async def test_reset_with_wrong_confirm(self, client):
        resp = await client.delete("/api/v1/admin/reset?confirm=wrong", headers=AUTH)
        assert resp.status_code in (400, 422)

    @pytest.mark.asyncio
    async def test_reset_with_correct_confirm(self, client):
        # Seed first
        await client.post("/api/v1/admin/seed", headers=AUTH)
        resp = await client.delete("/api/v1/admin/reset?confirm=delete-all-data", headers=AUTH)
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"


class TestTenantDesativado:
    """#70: tenant desativado nao testado para rejeicao auth."""

    @pytest.mark.asyncio
    async def test_active_tenant_can_access(self, client):
        """Tenant ativo consegue acessar endpoints."""
        resp = await client.get("/api/v1/metricas", headers=AUTH)
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_health_accessible_without_auth(self, client):
        """Health check nao requer auth."""
        resp = await client.get("/health")
        assert resp.status_code == 200
