from tests.conftest import AUTH


async def test_no_api_key_returns_401(client):
    resp = await client.get("/api/v1/clientes")
    assert resp.status_code == 401
    body = resp.json()
    assert body["status"] == 401
    assert "auth" in body["type"]


async def test_empty_api_key_returns_401(client):
    resp = await client.get("/api/v1/clientes", headers={"X-API-Key": ""})
    assert resp.status_code == 401


async def test_wrong_api_key_returns_401(client):
    resp = await client.get("/api/v1/clientes", headers={"X-API-Key": "wrong-key"})
    assert resp.status_code == 401


async def test_valid_api_key_passes(client):
    resp = await client.get("/api/v1/clientes", headers=AUTH)
    assert resp.status_code == 200


async def test_auth_error_follows_rfc9457(client):
    resp = await client.get("/api/v1/clientes")
    body = resp.json()
    assert "type" in body
    assert "title" in body
    assert "status" in body
    assert "detail" in body
