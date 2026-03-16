"""Auth attack vectors — bypass attempts, timing, enumeration."""
from tests.conftest import AUTH


# --- Missing/malformed auth ---

async def test_no_header_all_protected_endpoints(client):
    """Verify ALL protected endpoints reject requests without auth."""
    endpoints = [
        ("GET", "/api/v1/clientes"),
        ("POST", "/api/v1/clientes"),
        ("GET", "/api/v1/clientes/cli_fake"),
        ("PATCH", "/api/v1/clientes/cli_fake"),
        ("GET", "/api/v1/clientes/cli_fake/metricas"),
        ("GET", "/api/v1/faturas"),
        ("POST", "/api/v1/faturas"),
        ("GET", "/api/v1/faturas/fat_fake"),
        ("PATCH", "/api/v1/faturas/fat_fake"),
        ("GET", "/api/v1/cobrancas"),
        ("POST", "/api/v1/cobrancas"),
        ("GET", "/api/v1/cobrancas/fat_fake/historico"),
        ("PATCH", "/api/v1/cobrancas/cob_fake/pausar"),
        ("PATCH", "/api/v1/cobrancas/cob_fake/retomar"),
    ]
    for method, path in endpoints:
        resp = await client.request(method, path)
        assert resp.status_code == 401, f"{method} {path} returned {resp.status_code} without auth"


async def test_header_name_case_insensitive(client):
    """HTTP headers are case-insensitive per RFC 7230 — both forms work."""
    resp = await client.get("/api/v1/clientes", headers={"X-Api-Key": AUTH["X-API-Key"]})
    assert resp.status_code == 200  # correct per HTTP spec


async def test_auth_header_with_bearer_prefix(client):
    """Bearer prefix should not work — API expects raw key."""
    resp = await client.get(
        "/api/v1/clientes",
        headers={"X-API-Key": f"Bearer {AUTH['X-API-Key']}"},
    )
    assert resp.status_code == 401


async def test_auth_with_null_bytes(client):
    resp = await client.get("/api/v1/clientes", headers={"X-API-Key": "valid\x00key"})
    assert resp.status_code == 401


async def test_auth_with_very_long_key(client):
    """100KB key should not crash server."""
    resp = await client.get("/api/v1/clientes", headers={"X-API-Key": "A" * 100_000})
    assert resp.status_code == 401


async def test_auth_with_unicode_key(client):
    """Non-ASCII in headers — httpx may reject or server returns 401."""
    try:
        resp = await client.get("/api/v1/clientes", headers={"X-API-Key": "\u00e9\u00e7\u00e3"})
        assert resp.status_code == 401
    except UnicodeEncodeError:
        pass  # httpx correctly rejects non-ASCII header values


async def test_auth_with_sql_injection_in_key(client):
    resp = await client.get(
        "/api/v1/clientes",
        headers={"X-API-Key": "' OR 1=1--"},
    )
    assert resp.status_code == 401


async def test_auth_with_whitespace_key(client):
    resp = await client.get("/api/v1/clientes", headers={"X-API-Key": "   "})
    assert resp.status_code == 401


# --- Auth error response ---

async def test_auth_error_does_not_leak_valid_key(client):
    """Error response should not contain the expected key."""
    resp = await client.get("/api/v1/clientes")
    body = resp.text
    from app.config import settings
    assert settings.api_key not in body


async def test_auth_error_consistent_message(client):
    """Same error structure for missing vs wrong key (prevent enumeration)."""
    resp_missing = await client.get("/api/v1/clientes")
    resp_wrong = await client.get("/api/v1/clientes", headers={"X-API-Key": "wrong"})
    assert resp_missing.json()["title"] == resp_wrong.json()["title"]
    assert resp_missing.json()["type"] == resp_wrong.json()["type"]


# --- Health endpoint should NOT require auth ---

async def test_health_accessible_without_auth(client):
    resp = await client.get("/health")
    assert resp.status_code == 200


async def test_docs_accessible_without_auth(client):
    resp = await client.get("/docs")
    assert resp.status_code == 200


async def test_openapi_accessible_without_auth(client):
    resp = await client.get("/openapi.json")
    assert resp.status_code == 200
