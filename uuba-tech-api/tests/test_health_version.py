"""Testes do endpoint GET /health — verificacao de version."""


async def test_health_returns_version(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert "version" in body
    assert body["version"] == "0.1.0"
